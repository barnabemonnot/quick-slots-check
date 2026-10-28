#!/usr/bin/env python3
"""Opt-in preset extension; the original 32-slot ABI and vector file are unchanged."""
import argparse
import copy
import json
from pathlib import Path

from check import load_candidate

HERE = Path(__file__).resolve().parent
MAX = 2**64 - 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('candidate', nargs='?', default=str(HERE / 'ref.py'))
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    fn, label, module = load_candidate(args.candidate)
    validate = getattr(fn, 'validate_input', None) or getattr(module, 'validate_input', None)
    assert callable(validate), 'candidate must export validate_input with the preset extension'
    data = json.loads((HERE / 'minimal-vectors.json').read_text())
    assert data['slots_per_epoch'] == 8 and data['genesis_time'] == 0
    calls = 0
    raw_checks = 0
    fixed32_mismatches = 0

    def check(operation, value, options, expected):
        nonlocal calls, fixed32_mismatches
        try:
            actual = fn(operation, value, **copy.deepcopy(options))
        except ValueError as exc:
            actual = str(exc)
        assert type(actual) is type(expected) and actual == expected, (operation, value, actual, expected)
        calls += 1
        if type(expected) is int:
            # Negative control: the baseline/default 32-slot call must not silently
            # pass this separate fixture. Old candidates are not given new kwargs
            # by the original checker.
            old_options = {k: v for k, v in options.items() if k != 'slots_per_epoch'}
            try:
                old = fn(operation, value, **old_options)
            except ValueError as exc:
                old = str(exc)
            if old != expected:
                fixed32_mismatches += 1

    for scenario in data['scenarios']:
        if 'raw' in scenario:
            assert validate('normalize_forks', copy.deepcopy(scenario['raw']), slots_per_epoch=8) == scenario['schedule']
            raw_checks += 1
        options = dict(genesis_time=0, schedule=scenario['schedule'], slots_per_epoch=8)
        for case in scenario['cases']:
            s, t, e, d = case['slot'], case['start_ms'], case['epoch'], case['duration_ms']
            for op, value, expected in [('slot_start_ms',s,t),('epoch_at_slot',s,e),
                                         ('epoch_start_ms',e,case['epoch_start_ms']),
                                         ('ring_key',s,(t//1000)%8191)]:
                check(op,value,options,expected)
            for offset, expected in [(-1,s-1 if s else 'PRE_GENESIS'),(0,s),(1,s),(d-1,s),(d,s+1),(d+1,s+1)]:
                # Unsigned input contract rejects negative time before PRE_GENESIS.
                expected = 'INVALID_INPUT' if t+offset < 0 else expected
                check('slot_at_time_ms',t+offset,options,expected)
    assert fixed32_mismatches > 0

    def policy(kind, value, expected, spe=8):
        nonlocal raw_checks
        try:
            actual = validate(kind,copy.deepcopy(value),slots_per_epoch=spe)
        except ValueError as exc:
            actual = str(exc)
        assert type(actual) is type(expected) and actual==expected,(kind,actual,expected)
        raw_checks += 1

    policy('normalize_forks',{'legacy_ms':6000,'forks':[[0,5000],[0,4000]]},[[0,4000]])
    policy('normalize_forks',{'legacy_ms':6000,'forks':[[5,5000],[5,4000]]},[[0,6000],[5,4000]])
    policy('normalize_forks',{'legacy_ms':6000,'forks':[[MAX,5000]]},[[0,6000]])
    policy('normalize_forks',{'legacy_ms':6000,'forks':[[0,5000],[1,5000]]},[[0,5000],[1,5000]])
    fields={'HEZE_FORK_EPOCH':5,'SLOT_DURATION_MS':6000,'SLOT_DURATION_MS_HEZE':5000,'SLOTS_PER_EPOCH':8}
    policy('config',{'fields':fields},[[0,6000],[5,5000]])
    policy('config',{'fields':{**fields,'SLOTS_PER_EPOCH':32}},'CONFLICT')
    api={'SLOT_DURATION_MS':'6000','SECONDS_PER_SLOT':'6','SLOTS_PER_EPOCH':'8',
         'HEZE_FORK_EPOCH':'0','SLOT_DURATION_MS_HEZE':'5000',
         'SLOT_DURATION_SCHEDULE':[{'EPOCH':'0','SLOT_DURATION_MS':'5000'}]}
    policy('api',api,[[0,5000]])
    policy('api',{**api,'SLOTS_PER_EPOCH':'32'},'CONFLICT')
    policy('api',{**api,'SLOTS_PER_EPOCH':'08'},'INVALID_INPUT')
    # This future anchor fits with eight slots/epoch, but not with 32.
    late=MAX//8000
    value={'legacy_ms':1000,'forks':[[late,1000]]}
    policy('normalize_forks',value,[[0,1000],[late,1000]])
    policy('normalize_forks',value,'OVERFLOW',spe=32)
    policy('config',{'fields':{'HEZE_FORK_EPOCH':late,'SLOT_DURATION_MS':1000,'SLOT_DURATION_MS_HEZE':1000}},[[0,1000],[late,1000]])
    policy('api',{'SLOT_DURATION_MS':'1000','SECONDS_PER_SLOT':'1','SLOT_DURATION_SCHEDULE':[
                 {'EPOCH':'0','SLOT_DURATION_MS':'1000'},{'EPOCH':str(late),'SLOT_DURATION_MS':'1000'}]},[[0,1000],[late,1000]])
    check('slot_start_ms',late*8,dict(genesis_time=0,schedule=[[0,1000],[late,1000]],slots_per_epoch=8),late*8000)
    check('slot_at_time_ms',999,dict(genesis_time=1,schedule=[[0,6000]],slots_per_epoch=8),'PRE_GENESIS')
    for spe, expected in [(0,'INVALID_INPUT'),(-1,'INVALID_INPUT'),(True,'INVALID_INPUT'),
                          (1.5,'INVALID_INPUT'),('8','INVALID_INPUT'),(MAX+1,'OVERFLOW')]:
        check('epoch_at_slot',8,dict(genesis_time=0,schedule=[[0,6000]],slots_per_epoch=spe),expected)
        policy('normalize_forks',{'legacy_ms':6000,'forks':[]},expected,spe=spe)
    # One candidate with interleaved presets must not leak the previous choice.
    assert fn('epoch_at_slot',8,genesis_time=0,schedule=[[0,6000]]) == 0
    assert fn('epoch_at_slot',8,genesis_time=0,schedule=[[0,6000]],slots_per_epoch=8) == 1
    assert fn('epoch_at_slot',8,genesis_time=0,schedule=[[0,6000]]) == 0
    result={'candidate':label.replace(str(HERE)+'/', ''),'scenarios':len(data['scenarios']),
            'slot_cases':sum(len(s['cases']) for s in data['scenarios']),
            'arithmetic_checks':calls,'policy_checks':raw_checks,
            'fixed32_negative_control_mismatches':fixed32_mismatches,
            'scope':'Optional reference/policy ABI extension, not a minimal client or network run'}
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n')
    print('CHECKED minimal-preset extension:',json.dumps(result,sort_keys=True))


if __name__=='__main__':
    main()
