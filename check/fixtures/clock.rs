// Synthetic fixture for check/scan.py. Not taken from any project.
use std::time::Duration;

pub const SECONDS_PER_SLOT: u64 = 12;

pub fn slot_start(genesis_time: u64, slot: u64) -> u64 {
    genesis_time + slot * 12
}

pub fn deadline() -> Duration {
    // reveal deadline inside the slot
    Duration::from_millis(12000)
}

pub fn is_gloas(fork: ForkName) -> bool {
    fork == ForkName::Gloas
}

pub fn fixed_clock() -> u64 {
    slot_duration()
}
