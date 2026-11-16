# Changelog

## 1.0.3 — November 2026

- Keep Git commands whole when an option contains `$(...)` or backticks; treat the substitution as an unresolved value.
- Report `git config`/`git remote` changes next to staging without skipping the `.env` scan.
- Catch allowlist writes through `git diff/log --output` and through `.claude/` paths with wildcards or variables.
- Ask on pushes to a computed destination (`$(git branch --show-current)`, `$BRANCH`).
- Parse in linear time and once per command, so very long or deeply nested commands cannot push the hook past its timeout.
- Ask on subshells glued to a word, process substitutions, computed Git subcommands and very deep or very long `sh -c` nesting; recognize allowlist names split by quotes or written after `cd .claude`.

## 1.0.2 — November 2026

- Run the 1.0.0 reading of each command as a floor next to the new parser; the stricter answer wins.
- Check Git commands inside strings run by `eval`, `ssh`, `watch`, here-strings and pipes into a shell, in subshells and in substitutions.
- Treat more Git routing variables and options, exported `GIT_*` routing variables and `git config`/`git remote` changes in the same command as overrides.
- Ask when the shell writes a guardrail allowlist file.

## 1.0.1 — November 2026

- Recognize literal Git global options and quoted `-C` paths; review ambiguous repository/configuration overrides.
- Split background commands without breaking quoted or escaped path separators.
- Require whole-command deploy allowlist matches; confirm direct changes to policy files.
- Inspect nested Git env candidates and avoid exempting source files or public env files from key scanning.
- Normalize path allowlists; deny findings when the runtime cannot prompt.
- Skip shell comments, check `sh/bash/zsh -c` command strings, and ask when quoting or a `-C` directory cannot be resolved.
- Add regression tests using disposable local Git repositories and synthetic key shapes.

The hooks remain heuristics with the limits documented in the README.
