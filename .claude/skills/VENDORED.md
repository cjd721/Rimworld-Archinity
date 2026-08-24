# Vendored skills

These skills are copied from [mattpocock/skills](https://github.com/mattpocock/skills),
not installed as a Claude Code plugin, so they are ours to edit. Nothing updates
behind our back.

- **Source commit:** `6654f6b60cd9d5be8b54c6fafe44346dabeb3b76` (2026-08-24)
- **Set installed:** the 25 skills listed in the upstream `.claude-plugin/plugin.json`.
  Upstream `skills/deprecated/`, `skills/in-progress/` and `skills/misc/` were
  not taken.
- **Layout:** upstream nests them under `skills/engineering/` and
  `skills/productivity/`. They are flattened here to one directory per skill,
  which is what `.claude/skills/` expects.

## Local edits

- Upstream `code-review` is installed here as **`diff-review`**. Claude Code
  ships its own built-in `/code-review` (the one with `ultra`, `--fix`,
  `--comment`) and the two would collide. The frontmatter `name:` was changed,
  and the three cross-references that pointed at `/code-review` were repointed
  at `/diff-review`: `ask-matt/SKILL.md`, `implement/SKILL.md`, `tdd/SKILL.md`.

Re-apply that rename after any upstream pull.

## Updating

```bash
git clone --depth 1 https://github.com/mattpocock/skills.git /tmp/mp-skills
# copy the dirs named in /tmp/mp-skills/.claude-plugin/plugin.json, flattened,
# then re-apply the diff-review rename above.
```

`/setup-matt-pocock-skills` has not been run yet — it configures the issue
tracker, triage labels and docs location that the other skills read.
