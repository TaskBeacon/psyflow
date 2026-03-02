# Parameter Mapping

## Mapping Table

| Parameter ID | Config Path | Implemented Value | Source Paper ID | Evidence (quote/figure/table) | Decision Type | Notes |
|---|---|---|---|---|---|---|
| `condition_distribution` | `task.condition_weights` | `` | `paper_001` | `Condition proportion table` | `adapted` | If weighted generation is used, define explicit config weights aligned to `task.conditions`; otherwise mark even/default generation. |

Decision type values:

- `direct`
- `adapted`
- `inferred`
