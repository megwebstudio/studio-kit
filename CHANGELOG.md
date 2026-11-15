# Changelog

## 1.0.1 — November 2026

- Recognize literal Git global options and quoted `-C` paths; review ambiguous repository/configuration overrides.
- Split background commands without breaking quoted or escaped path separators.
- Require whole-command deploy allowlist matches; confirm direct changes to policy files.
- Inspect nested Git env candidates and avoid exempting source files or public env files from key scanning.
- Normalize path allowlists; deny findings when the runtime cannot prompt.
- Skip shell comments, check `sh/bash/zsh -c` command strings, and ask when quoting or a `-C` directory cannot be resolved.
- Add regression tests using disposable local Git repositories and synthetic key shapes.

The hooks remain heuristics with the limits documented in the README.
