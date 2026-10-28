# Checklists

| File | Use it when |
|---|---|
| [wrong-fixes.md](wrong-fixes.md) | You are reviewing a fix, or about to ship one. Ten wrong fixes that look correct. |
| [operator.md](operator.md) | You run or build software that touches slots or time. 15 checks by role. |
| [onchain-wrong-fixes.md](onchain-wrong-fixes.md) | You maintain contracts. 28 onchain wrong fixes, by class. |

Search patterns here are leads. Inspect the code path that runs. Run proposed tests in isolated fixtures or test
networks with synthetic inputs, never as live transactions.
