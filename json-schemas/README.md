# JSON Schemas for the research dashboard

Status: **proposal, version 1** (2026-11-09). The backend (orchestrator, compiler into the
UML / ns-3 inputs) does not read these documents yet; until it does, these files are the
contract between the dashboard and the future backend. Background and the mapping to what the
project runs today: [../scenario-format.md](../scenario-format.md).

The goal of this directory: **a scenario put together in the dashboard form is valid and can be
executed without further questions.** For that the dashboard needs three checks, in this order:

1. **JSON Schema** (the `*.schema.json` files): types, units, ranges, required fields, allowed values.
2. **Semantic rules** (`S-*`, `X-*` below): cross-field rules JSON Schema cannot express (an event
   must target an existing path, an event must happen before the end of the run, ...).
3. **Compatibility with an environment** (`E-*`): can the chosen environment run this scenario at all?

`validate.py` implements all three in Python as a **reference**; the rule ids and meanings
are the specification for the dashboard's own TypeScript checks.

## Contents

| file | document type (`schema` field) | who writes it | what it is |
|---|---|---|---|
| `common.schema.json` | — | — | shared definitions: ids, versions, seeds, environment types |
| `scenario.schema.json` | `mptcp-scenario/1` | **dashboard (scenario editor)** | test conditions: paths, loss, timed changes, traffic, receiver |
| `experiment.schema.json` | `mptcp-experiment/1` | **dashboard (experiment planner)** | what to run: scenarios × environments × algorithms × repetitions |
| `algorithm.schema.json` | `mptcp-algorithm/1` | backend (read-only catalogue) | an algorithm, its frozen parameter profiles, where it is implemented |
| `environment.schema.json` | `mptcp-environment/1` | backend (read-only catalogue) | an execution environment and its **capabilities** |
| `run.schema.json` | `mptcp-run/1` | backend | one execution, with a full snapshot of its configuration, status and results link |
| `examples/*.json` | all | — | valid examples (all pass `validate.py`) |
| `examples/invalid/*.json` | scenario | — | one deliberate mistake each; the file name is the rule it breaks: `<RULE>__<what>[@<env type>].json` |
| `validate.py` | — | — | reference validator and self-test |

## Concepts in one page

```
 Algorithm (catalogue) ─┐
                        ├──► Experiment ──freeze──► Run × N ──► Results (mptcp-metrics/1)
 Environment (catalogue)┤      (plan)                (one execution, immutable snapshot)
 Scenario (conditions) ─┘
```

* **Scenario** = *conditions only*: what the network looks like and what happens in it.
  It never names an algorithm or an environment. The same scenario (and the same seeds) is
  replayed for every algorithm, which is what makes a fair comparison possible.
* **Algorithm** = the thing being compared (LIA, OLIA, BALIA, wVegas = references; On-Off =
  own). Own algorithms are selected by a **profile**: a frozen, named parameter set. The
  dashboard does not edit algorithm parameters freely; a different parameter set is a different profile.
* **Environment** = where it runs: `uml` (User-Mode Linux emulation, real Linux MPTCP v0.96
  kernel), `dce` (ns-3 DCE with the Linux 4.1 MPTCP kernel), `ns3` (native ns-3 MPTCP
  model); later `rpi4` (hardware testbed) and `model` (Python/Octave). An environment publishes
  `capabilities`; the scenario editor uses them to disable options.
* **Experiment** = a plan: which scenario versions (optionally with a parameter sweep), which
  environments, which algorithms, how many repetitions.
* **Run** = one execution of (scenario variant, environment, algorithm, repetition). Created
  by the backend when the experiment is frozen, with a complete snapshot, so later edits of
  the catalogue never change history.
* **Seed / repetition**: every repetition has a seed. All randomness (which packets are lost,
  randomly generated delay changes, cross-traffic on/off periods) is derived from the seed, so
  repetition 3 of LIA and repetition 3 of On-Off see *exactly the same* conditions.

## Conventions (read before building forms)

* **Units are SI and part of the key name. Store SI, display whatever is convenient.**

  | suffix | unit | display in the UI as | factor (`x-display.factor`) |
  |---|---|---|---|
  | `_bps` | bit/s | Mbit/s | × 10⁻⁶ |
  | `_Bps` | **bytes**/s | kB/s or Mbit/s | × 10⁻³ / × 8·10⁻⁶ |
  | `_s` | seconds | s, or ms for delays | × 1 / × 10³ |
  | `_bytes` | bytes | KiB | ÷ 1024 |
  | `_pkts` | packets | packets | — |
  | probabilities (`probability`, `p_gb`, ...) | fraction 0..1 | % | × 100 |

  Every numeric property in the schema carries `x-unit` (stored unit) and most carry
  `x-display: {unit, factor}` (suggested display unit: `display = stored × factor`). Example: the
  user types 20 (Mbit/s) → store `bandwidth_bps: 20000000`; types 1 (%) → store `probability: 0.01`.
  The most common mistake is storing a percent as a probability; the schema rejects values > 1.

* **Delays are one-way.** `delay_s: 0.02` on a path gives an RTT of about 40 ms plus queueing.
  Label the field "one-way delay".
* **Ids**: catalogue ids `^[a-z0-9][a-z0-9_.-]{0,63}$`; path ids `^[A-Za-z0-9_-]{1,32}$`
  (`bottleneck` reserved). Generate path ids (`path1`, `path2`, ...) and let the user edit the `label`.
* **Versions**: `id` + `version` identify a scenario/experiment. A saved version is
  immutable; "edit" creates `version + 1`. Experiments pin a scenario version.
* **No unknown fields**: `additionalProperties: false` almost everywhere. Free-form only in
  `labels`, `backend_overrides`, algorithm `parameters`.
* **Write defaults explicitly.** `default` in the schema is documentation only. The dashboard
  should save the full document (e.g. `"loss": {"model": "none"}`, `"events": []`) so what is
  stored is what runs.
* **Omit what does not apply; do not write `null`.** E.g. no `bottleneck` key in disjoint mode. `null` is meaningful only where the schema says so: `read_schedule[].rate_Bps` (unlimited), experiment `repetitions`/`seeds` (use the scenario defaults), `implementation_hash`, run `results`.
* **Polymorphic objects use a discriminator field** inside `oneOf`: `loss.model`,
  `events[].action`, `generators[].type`, `traffic.type`, `seeds.strategy`. Render them as a
  select that switches the sub-form; each branch has a `title` for the select label.
* Schemas are JSON Schema **draft 2020-12** (checked with Ajv 8.17 in strict mode and Python `jsonschema` 4.26); `$id`s live under the placeholder base
  `https://mptcp-cc-poc.invalid/schemas/` and refer to each other by file name.

### Loading the schemas (TypeScript, Ajv)

```ts
import Ajv2020 from "ajv/dist/2020";
import addFormats from "ajv-formats";
import common from "./schemas/common.schema.json";
import scenario from "./schemas/scenario.schema.json";
// ... experiment, environment, algorithm, run

// strictRequired off: if/then and anyOf use "required" without repeating "properties"
const ajv = new Ajv2020({ allErrors: true, strict: true, strictRequired: false, allowUnionTypes: true });
addFormats(ajv);                                  // "date-time" in run records
ajv.addKeyword("x-unit");                         // our annotation keywords
ajv.addKeyword("x-display");
[common, scenario /*, ... */].forEach(s => ajv.addSchema(s));
const validateScenario = ajv.getSchema("https://mptcp-cc-poc.invalid/schemas/scenario.schema.json")!;
if (!validateScenario(doc)) console.log(validateScenario.errors);
// then the semantic rules S-* and, if an environment is chosen, E-*
```

For `oneOf` branches Ajv reports errors of every branch; show the user the errors of the
branch whose discriminator (`model`, `action`, `type`) matches.

---

## The scenario form, section by section

A scenario has these parts; the order below is a sensible order of form sections.
Full example: `examples/scenario-time-varying.json`.

### 1. General

| field | required | widget | meaning |
|---|---|---|---|
| `id` | yes | text (slug from the name) | stable identifier |
| `version` | yes | read-only | 1 on create, +1 on every saved edit |
| `name` | yes | text | short title |
| `description` | no | textarea | purpose of the test, what should happen |
| `labels` | no | key/value chips | for filtering (e.g. `family: time-varying`) |
| `duration_s` | yes | number, s | length of the data transfer (typ. 30–60 s; max 3600) |
| `statistics_window_s` | no | two numbers, s | `[from, to]` used for the summary numbers; before `from` is warm-up (TCP slow start). Default `[5, duration]` |

### 2. Topology

`topology.mode`:

* `disjoint` (default) — every path is an independent link with its own bottleneck. Typical case (Wi-Fi + LTE).
* `shared` — both paths meet in one common bottleneck behind their own access links. Used to
  test fairness to other traffic. Then **`topology.bottleneck` is required** (`bandwidth_bps`,
  `queue_pkts`, optional `delay_s`) and **`topology.cross_traffic` is allowed**: competing
  ordinary TCP flows (`cc: cubic|reno`, an access `delay_s`, and a fixed `schedule` of
  `{start_s, stop_s, flows}` and/or a random on/off `generator`).

In `disjoint` mode the schema forbids `bottleneck` and `cross_traffic` — hide them.

### 3. Paths (list; add/remove rows)

Each path is one MPTCP subflow. The format allows 1–8 paths; **all current environments
support exactly 2** (`capabilities.min_paths/max_paths`), so with an environment pre-selected the
"add path" button should stop at the limit.

| field | required | widget | meaning / typical values |
|---|---|---|---|
| `id` | yes | generated, editable | referenced by events and in results (`path_id`) |
| `label` | no | text | "Wi-Fi", "LTE", ... |
| `bandwidth_bps` | yes | number in Mbit/s | link rate, e.g. 20 Mbit/s → 20000000 |
| `delay_s` | yes | number in ms | **one-way** delay, e.g. 20 ms → 0.02 |
| `queue_pkts` | yes | integer | bottleneck queue length; 100 is the project's usual value. Changes results a lot: short queue → losses, long queue → delay (bufferbloat) |
| `loss` | no | loss sub-form (below) | artificial packet loss on this path |

**Loss sub-form** (`model` select):

| `model` | fields | when to use |
|---|---|---|
| `none` | — | no artificial loss (queue overflow still drops packets) |
| `bernoulli` | `probability` (%, stored as fraction) | independent random loss, e.g. 1 % |
| `gilbert-elliott` | `p_gb`, `p_bg`, `loss_good`, `loss_bad` | bursty loss. Show derived values: mean burst = 1/`p_bg` packets, mean loss = (`p_bg`·`loss_good` + `p_gb`·`loss_bad`)/(`p_gb`+`p_bg`) |
| `list` | `indices` | advanced (exact packets to drop), UML only — hide by default |

All loss models have `applies_to`: `data` (default; only data packets towards the receiver)
or `all` (both directions, ACKs too — used for a link failure).

**Jitter**: there is no per-packet jitter field (it would not be reproducible and it reorders
packets). Delay variation is a *generator* (section 5). The schema rejects unknown fields
such as `jitter_s` (`examples/invalid/SCHEMA__jitter-field.json`).

### 4. Timed events (list, sorted by time in the UI)

A change of one parameter at time `at_s` (seconds after the sender start). The new value holds
until the next change of the same parameter on the same target.

| `action` | value field | target |
|---|---|---|
| `set-loss` | `loss` (the loss sub-form) | a path |
| `set-bandwidth` | `bandwidth_bps` | a path, or `bottleneck` (shared mode) |
| `set-delay` | `delay_s` | a path, or `bottleneck` |
| `set-queue` | `queue_pkts` | a path, or `bottleneck` |

`target` should be a select filled from the current path ids (+ `bottleneck` when shared and
the action is not `set-loss`). If a path is deleted or renamed, the editor must update or flag
its events (rule S-TARGET).

**Presets worth offering** (they produce ordinary events):

| preset | events produced |
|---|---|
| path failure from t₁ to t₂ | `set-loss` at t₁ `{model: bernoulli, probability: 1, applies_to: all}`; `set-loss` at t₂ `{model: none}` |
| loss burst from t₁ to t₂ | `set-loss` at t₁ with Gilbert-Elliott; `set-loss` at t₂ `{model: none}` |
| rate dip from t₁ to t₂ | `set-bandwidth` at t₁ (low value); `set-bandwidth` at t₂ (original value) |
| RTT step | `set-delay` at t₁ |

Removing/adding an address, a new subflow or a handover are **not** supported by any
environment and are not part of the format.

### 5. Generators (randomised series, expanded per seed)

| `type` | fields | effect |
|---|---|---|
| `random-delay` | `target`, `start_s`, `every_s`, `min_delay_s`, `max_delay_s` | every `every_s` the one-way delay of the path is re-drawn uniformly from [min, max] — **this replaces "jitter"** |
| `outages` | `target`, `start_s`, `mean_interval_s`, `duration_s` | silent failures of length `duration_s`, random gaps with the given mean |

The backend turns generators into concrete events for each seed when the experiment is
frozen; the run record shows the result (`snapshot.expanded_events`).

### 6. Traffic (`traffic.type`)

* `bulk` — the sender always has data; the transfer is limited by network, algorithm and receiver.
* `media` — a video-like stream (`traffic.media`): `mode` `cbr|vbr`, `source` `live|stored`,
  `rate_Bps` (**bytes/s**; 2 Mbit/s = 250000), `fps`, `close` `hold|fin`, `start_delay_s`,
  optional viewer `pause_s: [from, to]`, `reverse` (second stream in the opposite direction).

### 7. Sender and receiver

| field | meaning |
|---|---|
| `sender.sndbuf_bytes` | fixed send buffer; 0 = autotuning (default) |
| `receiver.rcvbuf_bytes` | fixed receive buffer, disables autotuning; 0 = autotuning (default) |
| `receiver.rcvbuf_autotune_max_bytes` | upper limit of autotuning (Linux `tcp_rmem` max); omit for the platform default (16 MiB) |
| `receiver.read_schedule` | **how fast the receiving application reads**: a list of `{from_s, rate_Bps}`, each valid until the next; `rate_Bps: null` = unlimited, `0` = stops reading. Must start at `from_s: 0`. Example "full speed, 200 kB/s from 8 s, stalled 16–22 s, full speed again": `examples/scenario-receiver-limited.json` |

This replaces `receiverConsumptionMbps` of the earlier dashboard draft (note **bytes**/s, and
that it can change over time).

### 8. Repetitions and seeds (`defaults`)

`repetitions` (1–1000) and `seeds`: either `{strategy: sequence, start, step}` (repetition n
gets `start + (n−1)·step`) or `{strategy: explicit, values: [...]}` (exactly one distinct seed
per repetition). These are defaults; an experiment may override them. Suggest a sequence and
show the resulting seeds.

### 9. Advanced: `backend_overrides`

Raw fragments for one environment type (`uml`, `dce`, `ns3`, ...), merged into the compiled
input (e.g. MPTCP sysctls for UML). A scenario with overrides is environment-specific. Hide
this section by default and mark scenarios that use it.

---

## Semantic rules (must be checked in addition to the schema)

Errors block saving (or at least freezing); warnings are shown, not blocking.

| id | level | rule |
|---|---|---|
| `S-PATH-ID` | error | path ids are unique; `bottleneck` is not a path id |
| `S-TARGET` | error | every `events[].target` / `generators[].target` is an existing path id, or `bottleneck` only in shared mode and not for `set-loss`; generators target paths only |
| `S-EVENT-TIME` | error | `events[].at_s <= duration_s` |
| `S-EVENT-DUP` | error | no two events with the same (`at_s`, `target`, `action`) |
| `S-WINDOW` | error | `0 <= statistics_window_s[0] < statistics_window_s[1] <= duration_s` |
| `S-GEN` | error | generator `start_s < duration_s`; `min_delay_s <= max_delay_s`; outage `duration_s < duration_s` of the run |
| `S-READ` | error | `read_schedule` starts at `from_s = 0`, `from_s` strictly increasing, none after the end |
| `S-CROSS` | error | cross-traffic schedule: `start_s < stop_s <= duration_s` |
| `S-PAUSE` | error | media `pause_s`: `from < to <= duration_s` |
| `S-SEEDS` | error | an explicit seed list has exactly `repetitions` values (scenario defaults and experiment overrides) |
| `W-WARMUP` | warning | bulk traffic with a statistics window starting at 0 (slow start included) |
| `W-DELAY-TWICE` | warning | a path has both `set-delay` events and a `random-delay` generator |
| `W-BOTTLENECK` | warning | the shared bottleneck is not slower than all paths together (it never limits) |
| `W-QUEUE` | warning | a queue shorter than 10 packets |

## Compatibility with an environment (`E-*`)

When the user picks a target environment in the editor (or when an experiment is planned), compare
the scenario with `environment.capabilities`:

| id | check |
|---|---|
| `E-PATHS` | `min_paths <= len(paths) <= max_paths` |
| `E-TOPOLOGY` | `topology.mode` in `topology_modes` |
| `E-CROSS` | cross traffic only if `cross_traffic: true` |
| `E-TRAFFIC` | `traffic.type` in `traffic_types` |
| `E-EVENT` | every `events[].action` in `event_actions` |
| `E-GENERATOR` | every generator `type` in `generator_types` |
| `E-LOSS` | every loss model used (paths and `set-loss` events) in `loss_models`; its `applies_to` in `loss_applies_to` |
| `E-READ` | a limited `read_schedule` only if `read_schedule: true` |
| (exploratory) | a queue above `supported_queue_pkts_max`: allowed, but the run is labelled **exploratory** |

Current capabilities (`examples/environment-*.json`, to be confirmed by the backend):

| | `uml` | `dce` | `ns3` |
|---|---|---|---|
| paths | 2 | 2 | 2 |
| topology | disjoint, shared | disjoint, shared | disjoint |
| cross traffic | yes | yes | no |
| traffic | bulk, media | bulk | bulk, media |
| events | all four | loss, bandwidth, delay | loss, bandwidth, delay |
| generators | random-delay, outages | random-delay, outages | random-delay |
| loss models | none, bernoulli, gilbert-elliott, list | none, bernoulli, gilbert-elliott | none, bernoulli |

Beyond capabilities, the backend classifies each run as `supported`, `exploratory` or
`unsupported` (`tools/scope_check.py`), also by algorithm (e.g. wVegas results are not accepted
in native ns-3: `implementations[].status = unsupported`). Unsupported combinations are not run
and are **listed** in the plan preview, never silently dropped; exploratory runs carry the label
in every result view.

## Planning an experiment

`examples/experiment-loss-sweep.json`: one scenario with a **sweep** over the loss of path 2
(3 values), 2 environments, 3 algorithms, 10 repetitions.

* `scenarios[].sweep`: key = dotted path into the scenario (list indices as numbers:
  `paths.1.loss` is the loss of the second path), value = list of values; an object value
  replaces the whole sub-tree. Several keys → all combinations. Each combination is a
  *scenario variant* (`<id>@v<version>+<hash8>`) and must itself be a valid scenario (`X-SWEEP`).
* `algorithms[]`: `{id}` for a reference, `{id, profile}` for an algorithm with profiles (`X-PROFILE`); no duplicates (`X-ALG-DUP`).
* `repetitions` / `seeds`: `null` = take the scenario defaults.
* **Number of runs** = Σ over scenario variants × environments × algorithms that are compatible
  and available, of the repetitions. Example: 3 × 2 × 3 × 10 = **180**. Show this number and the
  list of rejected combinations before the user confirms.
* `status`: `draft → planned → frozen → running → completed | stopped | failed`. The dashboard
  sets `draft`/`planned`; `frozen` and later are set by the backend. After `frozen`, nothing but
  `status` changes.

| id | level | rule |
|---|---|---|
| `X-REF` | error | scenario (id+version), environment and algorithm ids exist in the catalogue |
| `X-PROFILE` | error | an algorithm with profiles needs an existing `profile`; one without profiles takes none |
| `X-ALG-DUP` | error | the same (algorithm, profile) at most once |
| `X-SWEEP` | error | every sweep path exists; every variant passes the schema and the S-rules |
| `W-PROFILE` | warning | the chosen profile is not `frozen` |

## Runs and results

`run.schema.json` / `examples/run-example.json`: identity (`run_id`, scenario variant,
environment, algorithm + profile + implementation hash, repetition, seed), `scope`,
`snapshot` (the resolved scenario, the generated events, the algorithm parameters, the
environment fingerprint), `condition_hash`, `status` (`pending → running → completed |
failed | interrupted`, later possibly `invalidated`), `attempts[]` and `results` (a link to
the metrics document, format `mptcp-metrics/1`, see [../metrics-format.md](../metrics-format.md)).

Runs with the same `condition_hash` saw identical conditions; comparisons between algorithms
should pair runs by it (same scenario variant, environment type and repetition).

## Validating locally

```bash
python3 docs/schemas/validate.py --selftest                       # all examples
python3 docs/schemas/validate.py my-scenario.json                 # schema + S-rules
python3 docs/schemas/validate.py my-scenario.json --env docs/schemas/examples/environment-ns3.json
python3 docs/schemas/validate.py my-experiment.json --catalog docs/schemas/examples   # + run count
```

The schema step needs the `jsonschema` package (≥ 4.18); without it only the semantic rules run.
Use the files in `examples/invalid/` as test cases for the dashboard's validation: each must
fail with exactly the rule in its name (rules after `@` need that environment type).

## Changing the schemas

A backward-compatible addition (a new optional field, a new enum value) keeps `/1`. Renaming or
removing a field, or changing a unit, creates `/2` (`mptcp-scenario/2`) with a migration. Add a
valid and an invalid example for every new rule and keep `validate.py --selftest` green.
