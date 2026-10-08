# AMLens

## Explainable Transaction Network Investigation

AMLens is an explainable transaction-network investigation tool for identifying suspicious transaction patterns and presenting evidence to investigators.

## Architecture

React → FastAPI → Analysis Engine → SQLite

## Team

- Dev 1 — Analysis Engine + Demo Data
- Dev 2 — Backend + Database + Integration
- Dev 3 — Frontend + Graph Interaction

## Project Structure

```text
analysis/    → transaction analysis and detection
backend/     → API, ingestion, persistence and integration
data/        → deterministic demo data
docs/        → contracts and API fixtures
frontend/    → React dashboard