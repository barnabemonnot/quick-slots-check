# Robust designs that do not break

These designs survived review with no BREAKS (CHECKED code). They are the template for every fix.

- Messaging bridges that read the EL `finalized` or `safe` tags.
- Oracles and keepers that count seconds and keep reorg depth in blocks.
- Intent systems that use only the execution layer.
- Rollups that read EL tags rather than beacon slots.
- Remote signers that count slots and epochs, not seconds.
- A block builder that takes the slot from `payload_attributes`.
- A proof generator that uses the real EL timestamp as the EIP-4788 key.
- A node that fetches blobs by versioned hash.

The common rule: take the slot or the time from its source. Do not compute one from the other with a constant.
