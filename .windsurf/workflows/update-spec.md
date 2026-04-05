---
auto_execution_mode: 0
description: 最新の agentskills.io の仕様やベストプラクティスを調査し、ore-skills のドキュメントや構造をアップデートする
---
You are an expert AI agent developer responsible for keeping the `ore-skills` repository up-to-date with the latest `agentskills.io` specifications and AI agent development best practices.

Your task is to autonomously research, propose, and apply updates to the repository structure, `SKILL.md` formats, and `CONTRIBUTING.md` guidelines.
Additionally, you should propose new skills that could be useful to the user based on external skill ecosystems and the user's actual workflows.

### Workflow Steps:

#### Part A: 仕様アップデート

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

#### Part B: おすすめスキル提案

5. **Survey external skill ecosystems**:
   - Read `docs/knowledge/external-skills-catalog.md` to get the list of known external skill sources.
   - Use `search_web` or `read_url_content` to browse the following sources for inspiration:
     - **Anthropic公式**: https://github.com/anthropics/skills (Creative, Development, Enterprise, Document)
     - **Vercel**: https://skills.sh/vercel-labs/agent-skills (Web開発ベストプラクティス)
     - **awesome-agent-skills**: https://github.com/skillmatic-ai/awesome-agent-skills
     - **SkillsMP**: https://skillsmp.com/ (マーケットプレイス)
     - **agentskill.sh**: https://agentskill.sh (44k+のスキル)
   - Look for skills that match common development workflows: code review, deployment, testing, documentation, refactoring, context management, etc.

6. **Cross-reference with the user's current setup**:
   - Read `docs/skill-catalog.md` to see what skills already exist and what's in the candidate pipeline.
   - Read `docs/knowledge/` files to understand what patterns and practices the user cares about.
   - Consider what the user frequently does in Windsurf (e.g., writing specs, managing Obsidian notes, working with YouTube content) and what could be abstracted into a reusable skill.

7. **Propose new skills**:
   - Present a ranked list of **3-5 skill candidates** with the following for each:
     - **スキル名**: proposed name (following naming conventions)
     - **概要**: what it does in 1-2 sentences
     - **着想元**: which external skill or pattern inspired this (with URL if applicable)
     - **ore-skills での差別化**: how this would be tailored to the user's specific workflow
     - **実装の規模感**: small (SKILL.md only) / medium (SKILL.md + scripts) / large (SKILL.md + Python implementation)
   - Do NOT propose skills that already exist in `docs/skill-catalog.md`.

8. **Implement approved skills** (if the user approves):
   - Use `scripts/create-skill.sh` or manually create the skill directory structure.
   - Write the `SKILL.md` with proper frontmatter and instructions.
   - Add supporting files (`references/`, `scripts/`) as needed.
   - Update `docs/skill-catalog.md` with the new entry.
   - Run `scripts/check-skill-health.sh` to validate.

#### Part C: 完了報告

9. **Report to the User**:
   - Summarize:
     - What specification updates were found and applied.
     - What new skills were proposed (and implemented, if any).
     - What external sources were consulted.
   - Update `docs/knowledge/external-skills-catalog.md` with the "Last Updated" date.

### Important Notes:
- Do NOT make destructive changes without high confidence that it matches the official specification.
- If you find no new updates or changes are necessary, simply report that the repository is already up-to-date.
- Keep the user's `Plan-First` workflow in mind: If the required changes are massive, present the plan first and wait for approval before executing step 4 or step 8.
- For skill proposals, prioritize **practical value** over novelty. The best skill candidates are things the user already does repeatedly that can be standardized.
- Do NOT blindly copy external skills. Adapt them to the user's workflow and ore-skills architecture.
