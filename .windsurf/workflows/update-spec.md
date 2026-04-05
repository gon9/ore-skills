---
auto_execution_mode: 0
description: 最新の agentskills.io の仕様やベストプラクティスを調査し、ore-skills のドキュメントや構造をアップデートする
---
You are an expert AI agent developer responsible for keeping the `ore-skills` repository up-to-date with the latest `agentskills.io` specifications and AI agent development best practices.

Your task is to autonomously research, propose, and apply updates to the repository structure, `SKILL.md` formats, and `CONTRIBUTING.md` guidelines.

### Workflow Steps:

1. **Research the latest specifications**:
   - Use the `search_web` or `read_url_content` tools to look up the latest updates on "agentskills.io specification", "Windsurf skills integration", or general AI agent skill architecture.
   - Look for changes in `SKILL.md` frontmatter requirements, directory structures, or recommended metadata fields.

2. **Analyze the current repository state**:
   - Review `CONTRIBUTING.md` and `docs/knowledge/` to understand the current rules.
   - Check existing skills in the `skills/` directory to see if they align with the new findings.

3. **Propose an Update Plan**:
   - Create a brief implementation plan using the `todo_list` tool.
   - The plan should include what needs to be changed (e.g., updating `CONTRIBUTING.md`, migrating existing `SKILL.md` files, or adding new validation scripts).

4. **Execute the Updates**:
   - Update `CONTRIBUTING.md` with the new rules.
   - Modify existing `SKILL.md` files or directory structures if the specification requires backward-incompatible changes.
   - If applicable, update the validation script (`scripts/check-skill-health.sh`) to enforce the new rules.

5. **Report to the User**:
   - Summarize what specifications were found, what changes were made, and ask the user to review the changes.

### Important Notes:
- Do NOT make destructive changes without high confidence that it matches the official specification.
- If you find no new updates or changes are necessary, simply report that the repository is already up-to-date.
- Keep the user's `Plan-First` workflow in mind: If the required changes are massive, present the plan first and wait for approval before executing step 4.
