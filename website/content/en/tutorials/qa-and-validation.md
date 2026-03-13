# QA, validation, and simulation gates

PsyFlow now expects more than “it runs once on my machine.” The maintained workflow has three complementary checks:

- QA mode for smoke execution and artifact validation
- simulation mode for responder-driven coverage
- static validation for task package, contract, and documentation checks

## QA mode

Run QA mode with:

```bash
psyflow-qa task-path --config config/config_qa.yaml
```

On a passing run, PsyFlow can promote maturity in `taskbeacon.yaml` and refresh the README maturity badge.

### Current QA artifact set

The framework-level artifact helper resolves these outputs under `outputs/qa/` by default:

- `qa_report.json`
- `static_report.json`
- `contract_report.json`
- `qa_trace.csv`
- `qa_events.jsonl`

Treat those as review artifacts, not incidental debug files.

## Validation

Use static validation even when you do not want to launch the task:

```bash
psyflow-validate task-path
```

The validator now covers much more than directory shape:

- config rules and config profile separation
- contract manifest checks
- reference-artifact requirements
- README structural expectations
- localization-safe runtime policy for participant-facing text

That last point matters. The framework now actively guards against hardcoded participant-facing text in runtime code when config-driven alternatives should be used.

## Simulation

Use simulation when you want deterministic or plugin-based responses without a real participant:

```bash
psyflow-sim task-path --config config/config_scripted_sim.yaml
```

If you need a task-specific sampler responder:

```bash
psyflow-sim task-path --config config/config_sampler_sim.yaml
```

## Responder protocol

The modern simulation layer revolves around a small set of concepts:

- `SessionInfo`
- `Observation`
- `Action`
- `Feedback`
- `ResponderProtocol`

Built-in options include:

- `NullResponder`
- `ScriptedResponder`

This is cleaner than older task-specific simulation hacks because the contract is explicit and pure Python.

## Runtime context helpers

Simulation also exposes runtime context tools such as:

- `RuntimeContext`
- `context_from_config()`
- `runtime_context()`
- `set_trial_context()`

`set_trial_context()` was recently generalized so it no longer depends on task-specific controller boilerplate for common deadline handling.

## Recommended gate sequence

For a task that is moving toward release:

```bash
psyflow-run .
psyflow-qa . --config config/config_qa.yaml
psyflow-sim . --config config/config_scripted_sim.yaml
psyflow-validate .
```

That sequence gives you:

- a human sanity check
- smoke execution with structured QA artifacts
- responder-based simulation coverage
- static contract and packaging validation

## What changed from older docs

The main updates are:

- no root `psyflow qa` or `psyflow sim` commands
- simulation profiles now use `config_scripted_sim.yaml` and `config_sampler_sim.yaml`
- QA and validation are stricter about contracts, reference artifacts, and localization-safe runtime text
