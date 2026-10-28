// Synthetic fixture for check/scan.py. Not taken from any project.
package chaintime

import "time"

const SecondsPerSlot = 12

var SlotDuration = 12 * time.Second

func SlotStart(genesis time.Time, slot uint64) time.Time {
	return genesis.Add(time.Duration(slot) * SlotDuration)
}

func CurrentSlot(now, genesisTime int64) int64 {
	return (now - genesisTime) / 12
}

func EpochSeconds(slot uint64) uint64 {
	return 384 // seconds per epoch
}

func ForkGate(f ForkName) bool {
	return f == ForkName.Gloas
}
