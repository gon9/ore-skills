# Specification Format Guide

## Overview
This reference describes the required format for specification documents checked by the Spec skill.

## Required Sections
A valid specification document MUST contain the following sections (headers):

- `# 概要` (Overview)
- `# 要件` (Requirements)
- `# 構成` (Architecture/Structure)

## `check_spec_file`

Validates a markdown string against the required format.

### Arguments
- `content` (str): The markdown content of the specification file.

### Returns
- `list[str]`: A list of strings describing any issues found. Returns an empty list if valid.

### CLI Usage
You can execute the script directly to check a local file.

```bash
uv run -m spec.checker <path_to_file>
```

Example:
```bash
uv run -m spec.checker docs/new_feature.md
```

### Output
- If issues are found: Exit code 1, issues printed to stdout.
- If no issues: Exit code 0, "No issues found." printed to stdout.
