// Synthetic fixture for check/scan.py. Not taken from any project.
export const SLOT_DURATION_MS = 12000;
const flags = { slotDurationOverride: true };

export function epochEta(epochs: number): number {
  // slot countdown
  return epochs * 384;
}

export function correct(slotStartMs: number, nowMs: number): number {
  return nowMs - slotStartMs; // time into slot from the true slot start: no hit expected
}
