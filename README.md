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
[psyflow website](https://taskbeacon.github.io/psyflow/).


## License

This project is licensed under the [MIT License](./LICENSE).
