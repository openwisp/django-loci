# AGENTS.md

## Project Overview

`django-loci` is a Django app that provides geographic and indoor mapping features used by OpenWISP modules.

Core code lives in `django_loci/`:

- `base/` contains abstract models and shared map/location behavior.
- `channels/`, `fields.py`, `storage.py`, `widgets.py`, `templates/`, and `static/` provide GIS, file, UI, and realtime helpers.
- Tests live in `django_loci/tests/` and `tests/`.

## Source of Truth

- Use `README.rst` and `docs/` for setup, package usage, and baseline test commands.
- Use `.github/workflows/ci.yml` for CI-tested dependencies, QA/test commands, env vars, and supported Python/Django versions.
- Use GitHub issue/PR templates when asked to open issues or PRs.

Follow the DRY principle: do not duplicate information or code across files.

If instructions conflict, repository config and CI workflows win first, docs next, and this file is supplemental.

## Development Notes

- Preserve public APIs, migrations, storage behavior, GIS field semantics, and integration points unless explicitly required.
- Mark user-facing strings for translation with Django i18n helpers in Django code.
- Place imports at the top of the file. Only defer imports when necessary (e.g., Django model imports inside functions or methods where the app registry is not yet ready).
- Avoid unnecessary blank lines inside function and method bodies.
- Update docs when behavior, settings, public APIs, setup steps, or supported versions change.

## Testing and QA

- For bug fixes, write the regression test first, run it against the unfixed code, confirm it fails for the expected reason, then implement the fix.
- Prefer method decorators for context managers that apply to the entire test method and would otherwise create unnecessary nesting, unless decorator ordering conflicts or the context manager requires data unavailable when the method is defined.
- Use targeted tests while iterating, then run the documented full test command before considering the change complete.
- Run `openwisp-qa-format` after editing when available.
- Prefer in-process tests so coverage tools can measure changed code.

## Django Notes

- Be careful with map/floor plan storage, geographic coordinates, file cleanup, channels updates, admin behavior, serializers, and migrations.
- When changing APIs or serializers, include tests for validation, permissions when applicable, and edge cases in geometry data.

## Security Notes

- Watch for unsafe file paths, unsafe uploads, invalid geometry data, and secrets.
- Preserve validation around floor plan images, map coordinates, storage paths, URLs, and uploaded/generated files.
- Write comments and docstrings only when they explain why code is shaped a certain way. Put comments before the relevant code block instead of scattering them inside it.

## Troubleshooting

- If setup, QA, or tests fail, check docs first, then compare with CI. If commands diverge, follow CI.

## Contributing Guidelines

- Before editing, inspect the relevant implementation, tests, documentation, and configuration. Follow existing repository patterns and do not invent behavior or requirements.
- Keep each contribution focused and change only the lines necessary for its goal. Do not include unrelated refactors, formatting churn, or generated and dependency-file changes unless explicitly required.
- Add or update focused tests for every behavior change. In repositories without a dedicated automated test suite, use the documented build and QA workflow as the equivalent behavior verification. For bug fixes, first reproduce the failure with a regression test when the repository's test setup allows it.
- Run the relevant targeted tests, builds, and documented QA checks, including `./run-qa-checks` when provided. Do not claim a change is complete when verification fails; report the failure or blocker.
- When requirements, intended behavior, or an unexpected failure are unclear, stop and seek clarification instead of making speculative changes.
- When starting work on a new issue, create a new branch from `master`. Use `issues/<issue-number>-<short-title>` for issue work; otherwise, use a short, descriptive branch name.
- Commit messages must be descriptive and use past tense. Past tense is a writing guideline that agents and contributors must follow; it is not checked automatically. For issue work, use an allowed prefix and a capitalized, past-tense subject ending with `#<issue-number>`, for example `[fix] Fixed perennial "modified" state #213`. Repeat the issue reference in the body with `Fixes`, `Closes`, `Resolves`, or `Related to` as appropriate. Use `openwisp-commit --check` to validate the structural commit convention and `cz -n cz_openwisp info` to view the allowed prefixes and message structure. If the repository's declared QA dependency predates these commands, install the development version with `pip install --upgrade "openwisp-utils[qa] @ https://github.com/openwisp/openwisp-utils/archive/refs/heads/master.tar.gz"` in the development environment.
- Add an explanatory commit body only for substantial changes, new features, or non-obvious bug fixes. The releaser automatically publishes the subject of `[feature]`, `[change]`, `[change!]`, `[deps]`, and `[fix]` commits, including scoped variants, in the changelog. Write those subjects in clear, user-friendly language suitable for release notes.
- Send new commits in response to review feedback instead of amending existing commits.
