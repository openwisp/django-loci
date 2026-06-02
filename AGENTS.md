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

- Keep changes focused. Avoid unrelated refactors and formatting churn.
- Preserve public APIs, migrations, storage behavior, GIS field semantics, and integration points unless explicitly required.
- Mark user-facing strings for translation with Django i18n helpers in Django code.
- Place imports at the top of the file. Only defer imports when necessary (e.g., Django model imports inside functions or methods where the app registry is not yet ready).
- Avoid unnecessary blank lines inside function and method bodies.
- Update docs when behavior, settings, public APIs, setup steps, or supported versions change.

## Testing and QA

- Add or update tests for every behavior change.
- For bug fixes, write the regression test first, run it against the unfixed code, confirm it fails for the expected reason, then implement the fix.
- Use targeted tests while iterating, then run the documented full test command before considering the change complete.
- Run `openwisp-qa-format` after editing when available.
- Run `./run-qa-checks` when present. Treat failures as blocking unless confirmed unrelated and reported.
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
