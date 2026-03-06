---
name: spec
description: Specification management capabilities. Use to validate design documents and ensuring format compliance.
---

# Spec Skill

## Overview
This skill provides tools for managing and validating specification documents.

## Capabilities

### Specification Checker
Validate that a markdown specification file contains all required sections.

- **Implementation**: `src/spec/checker.py`
- **Reference**: See [reference/format.md](reference/format.md) for format requirements and CLI usage.

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
