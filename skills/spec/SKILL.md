---
name: spec
description: Validates specification documents to ensure they contain required sections (概要, 要件, 構成). Use when checking design documents, specification files, or when the user mentions spec validation, document format checking, or requirements verification.
---

# Spec Skill

## Overview
This skill provides tools for managing and validating specification documents.

## Capabilities

### Specification Checker
Validate that a markdown specification file contains all required sections.

- **Implementation**: `src/spec/checker.py`
- **Reference**: See [references/format.md](references/format.md) for format requirements and CLI usage.

## Usage

### Checking a File
You can run the python module directly to validate a file.

```bash
uv run -m spec.checker <file_path>
```

Example:
```bash
uv run -m spec.checker docs/design.md
```
