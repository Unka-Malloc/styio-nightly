# Workflows

**Purpose:** Provide root-level reusable workflows and repo-local skills for styio-nightly delivery.

**Last updated:** 2026-04-23

## Scope

1. Keep mature reusable workflows under this root directory.
2. Treat `*.toml` as the machine-readable workflow format.
3. Keep Markdown files as human-facing explanations only.
4. Keep repo-local skills under `workflows/skills/` using `skill.toml`.
5. Keep docs mirrors under `docs/assets/workflow/` available for existing links.
6. Pair workflow changes with gates or validation commands.

## Entry Points

1. [ADD-REPO-FILE.md](./ADD-REPO-FILE.md)
2. [ADD-RESOURCE-IDENTIFIER.md](./ADD-RESOURCE-IDENTIFIER.md)
3. [ADD-SYNTAX-WITH-SKILLS.md](./ADD-SYNTAX-WITH-SKILLS.md)
4. [PROMOTE-NIGHTLY-PARSER-SUBSET.md](./PROMOTE-NIGHTLY-PARSER-SUBSET.md)
5. [CHANGE-BOOTSTRAP-ENV.md](./CHANGE-BOOTSTRAP-ENV.md)
6. [CHECKPOINT-WORKFLOW.md](./CHECKPOINT-WORKFLOW.md)
7. [DELIVERY-GATE.md](./DELIVERY-GATE.md)
8. [DOCS-GATE.md](./DOCS-GATE.md)
9. [FIVE-LAYER-PIPELINE.md](./FIVE-LAYER-PIPELINE.md)

## TOML Registry

See [workflows.toml](./workflows.toml).

## Inventory

See [INDEX.md](./INDEX.md).
