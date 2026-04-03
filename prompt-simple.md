Build a submission-ready take-home project for an AI Agent Driven Revenue Leakage Detection Platform using:

* Python + FastAPI
* React + TypeScript + Vite + Tailwind + React Query
* S3 for raw uploads
* DynamoDB single-table design
* separate item types for upload metadata, billing records, and analysis results
* Bedrock for selective reasoning only
* hybrid rule + LLM agent
* single orchestrator with tool-based internal modules
* structured JSON output
* unit tests for each small feature/module
* strong docs including `docs/decision-reasons.md`

Important architecture rules:

* keep raw billing data separate from generated AI analysis
* support analysis versioning/re-analysis
* denormalize summary fields onto record items for fast dashboard rendering
* deterministic rules perform calculations and leakage detection
* LLM handles reasoning, suggestions, and ambiguous cases only
* frontend must include upload, processed records table, flagged items, AI reasoning, severity filtering, summary metrics, and stretch features like chart/search/sort/pagination/high-risk section

Also generate:

* README
* architecture docs
* API docs
* testing docs
* decision reasons doc
* sample dataset
* strong unit tests across backend and frontend
