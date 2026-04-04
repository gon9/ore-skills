---
name: obsidian_utils
description: Manage and update personal indexes in an Obsidian Vault. Use to automatically compile index links from a vault directory into a single note.
license: MIT
compatibility: Requires Python 3.12+
---

# Obsidian Utils Skill

## Overview
This skill provides a suite of tools for maintaining an Obsidian vault. Currently, it includes a tool to auto-generate or update index files (MOCs) for a given directory.

## Usage

### 1. Update Index
Run the script to update the index of a specific directory `Personal/つれづれメモ.md`. You must pass the `--vault-dir` argument to specify the vault's root (where the `docs_obsidian` folder resides or similar structure).

```bash
uv run obsidian-update-index --vault-dir /path/to/vault
```

If no directory is specified, it will attempt to use a default path if executed from within the Obsidian repository context.

### Notes
- The updating mechanism relies on tags embedded in the markdown files (such as `#topic/...` or `#type/...`). If tags are not present, it attempts semantic guessing.
- Replaces content strictly between `<!-- INDEX_START -->` and `<!-- INDEX_END -->` markers in the target index file.
