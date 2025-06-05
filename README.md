# psyflow

This repository hosts the **psyflow** package.

## Publishing to PyPI

Releases are automated with GitHub Actions. Any push to the `main` branch
that contains `[publish]` in the commit message will trigger the
[`publish`](.github/workflows/publish.yml) workflow. The workflow builds
sdist and wheel via `python -m build` and uploads them to PyPI using the
`pypa/gh-action-pypi-publish` action. The upload requires a
`PYPI_API_TOKEN` secret configured in the repository.


