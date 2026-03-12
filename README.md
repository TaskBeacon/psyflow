# psyflow

**PsyFlow** is the canonical local framework for building auditable PsychoPy tasks inside a structured task package.

It focuses on a few concrete jobs:

- scaffold a canonical task layout
- provide reusable task primitives such as `BlockUnit`, `StimBank`, `StimUnit`, `SubInfo`, and `TaskSettings`
- support explicit runtime modes for human, QA, and simulation workflows
- validate task packages, contracts, reference artifacts, and localization-safe runtime behavior
- provide hardware-aware trigger I/O without binding task logic to one device protocol

## Current CLI entrypoints

The maintained commands are:

- `psyflow`
- `psyflow-run`
- `psyflow-qa`
- `psyflow-sim`
- `psyflow-validate`

Example workflow:

```bash
psyflow init my-task
cd my-task
psyflow-run .
psyflow-qa . --config config/config_qa.yaml
psyflow-sim . --config config/config_scripted_sim.yaml
psyflow-validate .
```

## Website

The published website is now a standalone Next.js static site under [`website/`](./website/), not the older Sphinx build.

Useful commands:

```bash
npm --prefix website run dev
npm --prefix website run build
npm --prefix website run lint
```

The website build also regenerates:

- CLI command data from `pyproject.toml`
- public export inventory from the Python package
- curated release summaries from `ChangLog.md`

## Documentation sources

- Site-owned content now lives in `website/content/`
- generated JSON data lives in `website/src/data/generated/`
- the legacy `docs/` tree remains only as migration/source material and is no longer the publishing pipeline

## Requirements

- Python >= 3.10
- Node.js for website development/build

## Changelog

See [`ChangLog.md`](./ChangLog.md).

## License

This project is licensed under the [MIT License](./LICENSE).
