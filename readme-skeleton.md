# AI Agent Driven Revenue Leakage Detection Platform

## Overview

Briefly describe the platform as a system for ingesting pricing/billing datasets, detecting revenue leakage, and surfacing AI-assisted reasoning through a dashboard.

## Tech Stack

* Backend: Python, FastAPI
* Frontend: React, TypeScript, Vite, Tailwind CSS, React Query
* Storage: S3, DynamoDB
* AI: AWS Bedrock
* Testing: pytest, Vitest, React Testing Library

## Architecture Summary

* S3 stores raw uploaded files
* DynamoDB uses a single-table design
* Billing records and analysis results are stored as separate item types
* A hybrid rule + LLM agent detects issues and generates reasoning
* The frontend provides upload, review, and investigation workflows

## Key Design Decisions

* Why DynamoDB
* Why single-table with separate analysis items
* Why Python + FastAPI
* Why hybrid rule + LLM
* Why selective LLM invocation

## Features

### Core

* CSV/JSON upload
* Processed records table
* Flagged leakage items
* AI reasoning
* Severity filtering
* Summary metrics

### Stretch

* Search
* Sorting
* Pagination
* Severity chart
* High-risk records section
* Analysis versioning support

## Project Structure

Give backend and frontend directory trees.

## Local Setup

### Backend

Commands to install and run.

### Frontend

Commands to install and run.

## Environment Variables

Document:

* AWS region
* S3 bucket
* DynamoDB table
* Bedrock model id
* local/dev flags

## Running Tests

### Backend

pytest command

### Frontend

vitest command

## API Summary

List main endpoints and their purpose.

## Sample Data

Explain included sample dataset and anomaly types.

## Assumptions and Trade-offs

Be explicit that:

* deterministic rules are the source of truth for calculations
* Bedrock is used for reasoning and suggestion generation
* DynamoDB summary fields are denormalized for UI performance
* some indexing/query patterns are simplified for take-home scope
