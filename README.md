# JAH Context Router — Conformance Harness

A local Python harness that parses a structured context-routing contract, validates its schemas and synthetic expected outputs, and checks captured routing results against those expectations. It does not perform semantic routing or call an inference API.

## Problem

Routing behavior is difficult to evaluate consistently when source eligibility, provenance, freshness, verification, missing context, and conflicts interact. This project provides a deterministic validation surface for a declared contract.

## Architecture

- `fixtures/CONTEXT_ROUTER_SYNTHETIC_CONTRACT.md` defines input/output schemas, vocabularies, 20 synthetic cases, and hard-fail assertions. Personal preference and project-state examples from the local evaluation were replaced with synthetic examples.
- `jah_router_harness/contract.py` parses the contract and extracts fixtures, enums, and assertions.
- `schema.py` validates input and result shape and vocabulary.
- `hf.py` evaluates hard-fail invariants.
- `runner.py` performs static checks and compares submitted captures.
- `cli.py` exposes `static` and `validate` commands.

## Scope and boundaries

The harness validates a supplied `routing_result`; it does not generate one. It does not choose tools, retrieve context, make external calls, authorize or execute actions, or prove a semantic router behaves correctly. The semantic invocations remain external and manual.

## Setup

Python 3.10+ is required.

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
```

## Static validation

```bash
python run_harness.py static --contract fixtures/CONTEXT_ROUTER_SYNTHETIC_CONTRACT.md
```

The static command checks parsing, exactly 20 case IDs, the 37-entry assertion catalog/registry, enum vocabularies, and expected-output schemas.

## Validate captures

```bash
python run_harness.py validate \
  --contract fixtures/CONTEXT_ROUTER_SYNTHETIC_CONTRACT.md \
  --captures ./captures
```

A capture must contain exactly an `id` and `routing_result`. The command reports missing captures explicitly. The included package has no semantic capture set, so a full conformance verdict is not claimed.

## Security and privacy

The public fixture contract contains synthetic examples only. Do not add personal context, real customer or employee data, credentials, private instructions, or production captures. Keep local captures and generated reports out of version control.

## Verification

Static validation is run in a local staging copy before publication. No semantic routing calls or paid API calls are made.

## Status

Independent engineering / R&D. A conformance harness, not a semantic router or deployed service.

## Ownership and license

Created and owned by Mohamed Gamal. No reuse license is currently granted; contact the owner for permission.
