# Principle 4: Link to code properly

Never duplicate large code blocks. Link to the source instead. Code changes frequently; docs do not.

## Linking to Documentation Files

Use relative paths within the `docs/` folder.

**DO:**

- `[Principle 1: Docs describe what exists](principle-1-no-fiction.md)`
- `[Principle 5: Format and consistency](principle-5-format-style.md)`

**DON'T:**

- Relative paths to code outside docs: `[config](../../pyproject.toml)`
- Broken anchor attempts to non-doc files

## Linking to Code and Non-Documentation Files

Use full GitHub permalinks. Static documentation sites cannot resolve relative paths outside `docs/`.

**DO:**

- `https://github.com/HYP3R00T/shiftcraft/blob/main/pyproject.toml`
- `https://github.com/HYP3R00T/shiftcraft/blob/main/zensical.toml`

**DON'T:**

- Relative paths: `[setup.sh](../../scripts/setup.sh)`
- Links without protocol or host: `blob/main/file.py`
