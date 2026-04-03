# Documentation

This folder contains focused project documentation that complements the root `README.md`.

## Documents

- `docs/architecture.md` - system structure, data flow, and current runtime boundaries
- `docs/api.md` - backend endpoints, request parameters, and response shapes
- `docs/testing.md` - test layout, commands, and what each suite covers
- `docs/decision-reasons.md` - implementation decisions and current trade-offs
- `docs/sample-data.md` - bundled sample dataset and the anomaly scenarios it covers

## Scope

These docs describe the repository as it is currently implemented:

- ingestion and normalization in the backend
- in-memory API behavior for uploads, records, analysis lookup, and dashboard summary
- structured leakage incidents returned by analysis
- frontend upload and dashboard flows with table, severity filter, client-side search, pagination, and severity chart
