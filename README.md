# psyflow

**psyflow** is a small framework that helps build modular cognitive and
behavioural experiments on top of
[PsychoPy](https://www.psychopy.org/).  It bundles a collection of helper
classes and utilities so you can focus on experimental logic rather than
boilerplate.

## Key components

- **BlockUnit** – manage blocks of trials and collect results
- **StimUnit** – present a single trial and log responses
- **StimBank** – register and build stimuli from Python functions or YAML
  definitions
- **SubInfo** – gather participant information via a simple GUI
- **TaskSettings** – central configuration object for an experiment
- **TriggerSender** – send triggers to external devices (e.g. EEG/MEG)

The package also provides a command line tool `psyflow-init` which
scaffolds a new project using the bundled cookiecutter template.

Comprehensive documentation and tutorials are available on the
[GitHub&nbsp;Pages site](https://taskbeacon.github.io/psyflow/).

## Publishing to PyPI

Releases are automated with GitHub Actions. Any push to the `main` branch
that contains `[publish]` in the commit message will trigger the
[`publish`](.github/workflows/publish.yml) workflow. The workflow builds
sdist and wheel via `python -m build` and uploads them to PyPI using the
`pypa/gh-action-pypi-publish` action. The upload requires a
`PYPI_API_TOKEN` secret configured in the repository. 


