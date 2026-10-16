# Ω JAH — Context Router v0.1 — Public Synthetic Conformance Contract

- Artifact Status: `CONTRACT_AND_EVAL_CANDIDATE_R5`
- Component: `CONTEXT_ROUTER`
- Version: `v0.1-R5`
- Discovery Gate: `PASS`
- Router Justification: `JUSTIFIED`
- R4 Fixture Parse/Schema Check: `PASS_20_OF_20`
- Canonical Status: `NOT_CANON`
- Interface Freeze: `NOT_YET`
- Implementation Status: `NOT_STARTED`

R5 is the narrow freeze-closure revision of R4. It resolves only the five R4 closure blockers: semantic identity for non-`AVAILABLE` targets, truthful deferred-conflict serialization, deterministic all-select behavior for equal eligible sources, role-true external retrieval reason semantics, and a self-contained hard-fail assertion catalog.

It does not redesign Router ownership, modify the Kernel, add an architectural layer, implement routing code, choose tools or modes, grant execution authority, execute actions, or promote this artifact to canon.

## 1. CONTRACT_GOALS

1. Preserve R4 architecture, enums, ownership boundaries, and the existing 20 eval IDs/categories.
2. Make every source target semantically matchable even when its content is not `AVAILABLE`.
3. Keep source content access truthful: semantic target identity is not content retrieval.
4. Preserve terminal missing-gate precedence while serializing real selected-source conflicts truthfully.
5. Make equivalent eligible source treatment deterministic without using opaque refs or input order as tie-breakers.
6. Keep freshness/currentness in task semantics plus `FRESHNESS_STATE`, not in source-class or retrieval-domain reason names.
7. Make the artifact self-contained for a machine harness by defining every referenced hard-fail assertion ID.
8. Preserve role-only source classes, governing-only current user intent, Kernel governing-plane separation, non-routable inference, source-unit binding, homogeneous source granularity, metadata-dimension separation, opaque refs, canon-instance role, role-valid verification, currentness eligibility, universal partitioning, mixed missing-state dominance, one terminal action, explicit serialization, and no numeric context budget.
9. Preserve Router non-ownership of Verification, Tool Router, Mode Engine, execution authority, execution, and canon mutation.
10. Do not freeze or implement the interface in this artifact; R5 must first pass the seven-point freeze exit check.

## 2. ROUTING_INPUT_SCHEMA

The R5 input envelope is:

```yaml
routing_input:
  current_user_intent:
    instruction: <governing task instruction>
    scope_ref: <opaque scope reference | NONE>
  source_items:
    - source_ref: <opaque source-instance reference>
      source_class: <SOURCE_CLASS>
      scope_ref: <opaque source project/scope reference | NONE>
      provenance: <PROVENANCE_STATE>
      availability: <AVAILABILITY_STATE>
      freshness: <FRESHNESS_STATE>
      upstream_verification: <VERIFICATION_STATE>
      canon_instance_role: <CANON_INSTANCE_ROLE | null>
      source_target:
        description: <non-empty task-readable semantic target descriptor>
      source_unit:
        claims:
          - <task-readable semantic claim/content stub>
```

Field rules:

- `current_user_intent` is mandatory governing input and is not a routable source.
- `source_items` is the complete finite candidate set exposed to Router for one decision. Candidate discovery is upstream/out of scope.
- `source_ref` is opaque and unique within one input.
- `source_target` is mandatory on every source item.
- `canon_instance_role` is mandatory as a field: one role for `PROJECT_CANON`; `null` for every other source class.
- `source_unit` is mandatory as a field. For `AVAILABLE`, it is non-null with at least one readable claim. For non-`AVAILABLE`, it may be `null`.
- Input ordering is non-semantic.
- No tool, connector, reasoning mode, execution-authority, platform-permission, execution, canon-mutation, or numeric-budget field is added.

### Current-truth input-totality precondition

If current user intent materially requires current truth and no `AVAILABLE` source with `freshness=CURRENT` can satisfy a required current claim, the input MUST expose the exact required semantic target as a `RETRIEVABLE`, `INACCESSIBLE`, or `UNAVAILABLE` source item. Router MUST NOT invent a target `source_ref`, parse target semantics from ref spelling, silently reclassify an available stale/unknown item as missing, or claim current truth from an explicitly stale item.

## 3. SOURCE_TARGET_MODEL

`source_target` exists solely to identify what a source item semantically represents before its content is necessarily readable.

Frozen shape:

```yaml
source_target:
  description: <non-empty task-readable semantic target descriptor>
```

Rules:

1. `source_target.description` is mandatory for every source item, including `AVAILABLE` items.
2. It describes the task-relevant target/context/claim domain represented by the item; it is not the source content itself.
3. It carries no authority, provenance, availability, freshness, verification, canon-instance precedence, or execution semantics. Those remain in their dedicated fields/rules.
4. It MUST NOT be treated as evidence that the represented content was read, retrieved, verified, or found.
5. For `AVAILABLE` items, semantic reasoning may use readable `source_unit.claims`; `source_target` does not replace the unit.
6. For non-`AVAILABLE` items, `source_target.description` is sufficient to match current task requirements to the exact known target without reading unavailable content.
7. No semantic meaning is derived from `source_ref` text when `source_target` exists.
8. `source_target` adds no discovery, storage, retrieval, or verification responsibility to Router.

## 4. SOURCE_UNIT_BINDING

1. Each `source_ref` binds exactly one source item and one routing-relevant source unit for the lifetime of one routing decision.
2. The binding is immutable during the decision.
3. An `AVAILABLE` unit is directly readable by Router without retrieval or Tool Router invocation.
4. A non-`AVAILABLE` unit may have `source_unit: null`; Router may use only the semantic target descriptor plus supplied metadata for matching until content becomes available.
5. Relevance, silence, contradiction, sufficiency, history/comparison role, and claim semantics for `AVAILABLE` items use the bound unit plus metadata; identifier text carries no semantics.
6. The binding is an interface precondition, not a content-storage/retrieval layer.
7. Router does not mutate source units.
8. Every output source reference resolves to the exact input item.

## 5. SOURCE_ITEM_GRANULARITY

One `source_item` represents one routing-relevant context unit / homogeneous claim set.

The following apply uniformly to the whole item:

- `source_class`
- `scope_ref`
- `provenance`
- `availability`
- `freshness`
- `upstream_verification`
- `canon_instance_role`
- the target semantics described by `source_target`

If one physical artifact contains claims with materially different metadata or routing roles, upstream must expose separate source items/refs. R5 adds no claim engine and no architectural layer.

## 6. ROUTING_RESULT_SCHEMA

The R5 output shape remains:

```yaml
routing_result:
  action: <ROUTING_ACTION>
  selected_sources:
    - source_ref: <input source_ref>
      source_class: <SOURCE_CLASS>
      provenance: <PROVENANCE_STATE>
      freshness: <FRESHNESS_STATE>
      upstream_verification: <VERIFICATION_STATE>
      canon_instance_role: <CANON_INSTANCE_ROLE | null>
  exclusions:
    - source_ref: <input AVAILABLE source_ref>
      source_class: <SOURCE_CLASS>
      reasons:
        - <EXCLUSION_REASON>
  reason_codes:
    primary: <RUNTIME_REASON_CODE>
    supplemental:
      - <RUNTIME_REASON_CODE>
  unresolved_conflict: <boolean>
  conflict_source_refs:
    - <input selected AVAILABLE source_ref>
  missing_context:
    state: <MISSING_CONTEXT_STATE>
    required_sources:
      - source_ref: <input non-AVAILABLE source_ref>
        source_class: <SOURCE_CLASS>
```

Serialization rules:

- every field is present;
- empty collections serialize as `[]`;
- `unresolved_conflict` is explicit;
- `missing_context.state` is explicit;
- exactly one primary runtime reason is emitted;
- supplemental reasons are always present;
- selected metadata exactly copies input metadata;
- list ordering is non-semantic, but membership is exact.

A selected source in a non-`USE_CONTEXT` result is usable partial context carried forward. Selection never claims the task is resolved; the terminal action states whether further context work is required.

## 7. GOVERNING_INPUTS

### `CURRENT_USER_INTENT`

`CURRENT_USER_INTENT` exists only as `routing_input.current_user_intent`. It is the highest task-level governing input and MUST NOT appear in `source_items[*].source_class`, `selected_sources`, `exclusions`, `conflict_source_refs`, or `missing_context.required_sources`.

User-supplied project facts distinct from the task instruction are represented upstream as source items, normally `PROJECT_EVIDENCE + USER_STATED`.

### Kernel governing plane

`JAH_KERNEL_CANON_v1.0` remains a behavioral governing plane, not routable project evidence. It is never serialized as a source, selection, exclusion, conflict ref, or missing-context target. Project truth and Kernel behavior remain separate ownership planes.

## 8. ROUTABLE_SOURCE_MODEL

`SOURCE_CLASS` is exactly:

```text
PROJECT_CANON
PROJECT_EVIDENCE
PERSONAL_CONTINUITY
EXTERNAL_CONTEXT
```

- `PROJECT_CANON` — canonical owner of project truth for its declared scope; class alone implies neither freshness nor verification.
- `PROJECT_EVIDENCE` — non-canonical project evidence, including reports, logs, chats, manifests, and user-stated project facts.
- `PERSONAL_CONTINUITY` — history/preferences/continuity; never project-truth authority merely because it is current or verified.
- `EXTERNAL_CONTEXT` — externally owned facts; it does not silently become project truth and does not imply currentness by class name.

Non-source objects include current user intent, Kernel governing context, `FRESH_VERIFIED_STATE`, inference, missing sentinels, tool names, reasoning modes, and execution actions.

## 9. PROVENANCE_MODEL

`PROVENANCE_STATE` is exactly:

```text
USER_STATED
RETRIEVED
REMEMBERED
UNKNOWN
```

Provenance describes origin, not availability, freshness, verification, authority, or currentness eligibility. `ACTIVE` is not provenance.

## 10. AVAILABILITY_MODEL

`AVAILABILITY_STATE` is exactly:

```text
AVAILABLE
RETRIEVABLE
INACCESSIBLE
UNAVAILABLE
```

- `AVAILABLE` — content is directly usable in this routing decision.
- `RETRIEVABLE` — content is unavailable now, but a downstream retrieval path is declared possible.
- `INACCESSIBLE` — the exact semantic target is known but inaccessible in the current runtime/retrieval envelope.
- `UNAVAILABLE` — the exact semantic target is known but no usable/routable path is declared for this decision.

Only `AVAILABLE` items may be selected. Non-`AVAILABLE` items never appear in `exclusions`; if materially required, they appear in `missing_context.required_sources`.

## 11. FRESHNESS_MODEL

`FRESHNESS_STATE` is exactly:

```text
CURRENT
STALE
UNKNOWN
```

1. For a task that materially requires current truth, an item with `STALE` MUST NOT satisfy the requirement regardless of source role, verification state, or canon-instance role.
2. `CURRENT` is currentness-eligible, subject to scope, role, verification, relevance, and contradiction rules.
3. `UNKNOWN` does not prove currentness and is never silently promoted to `CURRENT`; it may still be selected as safe contextual/partial material when the task does not require it to establish current truth.
4. If current truth is required and no eligible `CURRENT` source is `AVAILABLE`, the exact needed target must already exist in input as non-`AVAILABLE`.
5. `STALE` remains eligible when history, prior state, or change-over-time comparison is explicitly requested.
6. Router consumes freshness metadata; it does not compute timestamps or freshness.

## 12. VERIFICATION_METADATA_BOUNDARY

`VERIFICATION_STATE` is exactly:

```text
VERIFIED
NOT_VERIFIED
UNKNOWN
```

Verification is upstream-owned/read-only. Router MUST NOT perform verification, synthesize `VERIFIED`, infer verification from retrieval/availability/freshness/canon status, or treat verification as execution permission.

Verification validates the exact homogeneous claim set represented by a source item. It does not transform source role, override scope, or erase explicit `STALE` currentness ineligibility.

## 13. CANON_INSTANCE_ROLE_MODEL

`CANON_INSTANCE_ROLE` is exactly:

```text
STANDARD
DEPLOYED_COPY
ROOT_OF_TRUST
```

Rules:

- meaningful only for `PROJECT_CANON`;
- supplied upstream/read-only;
- never inferred from `source_ref`, filename, path, `source_target`, or content wording;
- `ROOT_OF_TRUST > DEPLOYED_COPY` only for competing instances of the same canonical truth under the existing deployment rule;
- higher instance role never invents access: an `INACCESSIBLE ROOT_OF_TRUST` remains inaccessible;
- no additional ordering for `STANDARD` is invented unless an existing project rule supplies it.

## 14. SOURCE_REFERENCE_MODEL

`source_ref` is opaque and authority-free:

1. unique within one routing input;
2. stable for one routing decision;
3. used only to bind input source instances to output references;
4. no authority, scope, provenance, availability, freshness, verification, target semantics, or content semantics are derived from lexical form;
5. every output ref exists in input;
6. multiple refs may share one source class and one semantic target;
7. Router never invents a missing target ref;
8. neither lexical ordering nor input ordering is an authority/tie-break rule.

## 15. AUTHORITY_ROLE_AND_CURRENTNESS_PRECEDENCE

R5 applies eligibility before authority.

For each task requirement:

1. apply current user intent and scope;
2. apply scope eligibility;
3. match semantic requirements using `source_target` and, where `AVAILABLE`, readable `source_unit.claims`;
4. apply currentness eligibility for that requirement;
5. apply role-valid verification and source-role precedence among remaining eligible candidates;
6. apply canon-instance role when competing items represent the same canonical truth;
7. retain all equally eligible sources unless a truthful exclusion reason applies;
8. surface any real unresolved conflict among selected eligible sources, subject only to terminal missing-gate precedence.

Project-truth role order among eligible sources remains:

`role-valid CURRENT+VERIFIED project claim > PROJECT_CANON > PROJECT_EVIDENCE > PERSONAL_CONTINUITY`

Constraints:

- a `STALE PROJECT_CANON` is not an eligible current-truth winner merely because it is canon;
- stale canon may be selected for requested history/comparison;
- verification never cross-promotes `PERSONAL_CONTINUITY` or `EXTERNAL_CONTEXT` into project-truth roles;
- external context is authoritative only for externally owned facts;
- inference is downstream and never a routable fallback;
- `source_target` identifies semantics but creates no authority;
- equal eligibility is not resolved by arbitrary ref/input order.

## 16. MISSING_CONTEXT_MODEL

`MISSING_CONTEXT_STATE` is exactly:

```text
NONE
REQUIRED
INACCESSIBLE
UNRESOLVABLE_WITH_AVAILABLE_SOURCES
```

Dominance for materially required non-`AVAILABLE` sources is:

`UNRESOLVABLE_WITH_AVAILABLE_SOURCES > INACCESSIBLE > REQUIRED > NONE`

Mapping:

- any required `UNAVAILABLE` item -> `UNRESOLVABLE_WITH_AVAILABLE_SOURCES`;
- otherwise any required `INACCESSIBLE` item -> `INACCESSIBLE`;
- otherwise any required `RETRIEVABLE` item -> `REQUIRED`;
- no materially required non-`AVAILABLE` item -> `NONE`.

When state is non-`NONE`, `missing_context.required_sources` contains every materially required non-`AVAILABLE` input item, across all lower-dominance states as well. When state is `NONE`, `required_sources=[]`.

`source_target.description` is the semantic basis for identifying which non-`AVAILABLE` items are materially required; Router does not read unavailable content or derive meaning from `source_ref`.

## 17. DECISION_VOCABULARY

`ROUTING_ACTION` is exactly:

```text
USE_CONTEXT
RETRIEVE_CONTEXT
ASK_USER
SURFACE_CONFLICT
```

- `USE_CONTEXT` — no higher missing gate remains and selected/current-intent context is sufficient.
- `RETRIEVE_CONTEXT` — at least one materially required source is `RETRIEVABLE`, and no required source is `INACCESSIBLE` or `UNAVAILABLE`.
- `ASK_USER` — at least one materially required source is `INACCESSIBLE` or `UNAVAILABLE`.
- `SURFACE_CONFLICT` — no materially required non-`AVAILABLE` source exists and selected `AVAILABLE` context contains a real unresolved material conflict.

No fifth terminal action is added. Exclusion and conflict serialization remain metadata around the single terminal action.

## 18. TERMINAL_GATE_PRECEDENCE

One terminal action is chosen by this precedence:

```text
1. required UNAVAILABLE
2. required INACCESSIBLE
3. required RETRIEVABLE
4. unresolved material conflict among selected eligible AVAILABLE sources
5. otherwise USE_CONTEXT
```

| Highest gate present | `action` | `missing_context.state` |
|---|---|---|
| required `UNAVAILABLE` | `ASK_USER` | `UNRESOLVABLE_WITH_AVAILABLE_SOURCES` |
| else required `INACCESSIBLE` | `ASK_USER` | `INACCESSIBLE` |
| else required `RETRIEVABLE` | `RETRIEVE_CONTEXT` | `REQUIRED` |
| else unresolved selected conflict | `SURFACE_CONFLICT` | `NONE` |
| else | `USE_CONTEXT` | `NONE` |

A higher missing gate dominates only the **terminal action**. It does not make a selected-source conflict false. Conflict existence is serialized independently under Section 20.

## 19. UNIVERSAL_SELECTION_AND_EXCLUSION_RULES

### Universal selection rule

For every terminal action, `selected_sources` contains every input source item that is:

1. `AVAILABLE`;
2. materially required or materially useful for the eventual task represented by current intent;
3. scope-eligible;
4. safe for the role it is being asked to play;
5. not currentness-ineligible for that role;
6. not truthfully excluded as superseded/lower-authority for the same required claim when it cannot contribute independently;
7. not irrelevant.

A source contributes independently when, for example, it is explicitly required for comparison/history or it is needed to truthfully represent an unresolved selected conflict. A missing preferred source does not by itself justify discarding readable material that remains independently useful.

`RETRIEVE_CONTEXT` and `ASK_USER` therefore may—and when the rule matches, MUST—carry partial selected context.

### Equal eligible source rule

If multiple `AVAILABLE` sources are equally eligible, materially relevant, non-conflicting, and no truthful exclusion reason applies, **select all of them**.

- Do not choose one by `source_ref` spelling.
- Do not choose one by input order.
- Do not create a hidden authority tie-break.
- Do not add `REDUNDANT` to the exclusion vocabulary.

This is a narrow determinism rule: truthful equal selection outranks arbitrary trimming. Equal eligible sources that materially conflict are also selected, with conflict serialized under Section 20.

### Universal AVAILABLE partition

Every `AVAILABLE` input source appears in exactly one of `selected_sources` or `exclusions`. Every non-`AVAILABLE` source appears in neither. No item may appear in both.

### Exclusion reasons

The exclusion vocabulary remains exactly:

```text
PROJECT_BOUNDARY
STALE
LOWER_AUTHORITY
IRRELEVANT
```

Application:

1. `PROJECT_BOUNDARY` — outside current task scope and no explicit cross-scope comparison is requested; stop further exclusion classification.
2. `IRRELEVANT` — scope-eligible but not materially needed/useful for the eventual task; stop freshness/authority classification.
3. `STALE` — explicitly stale while being considered for a role that materially requires current truth. Historical use does not receive this exclusion.
4. `LOWER_AUTHORITY` — competes for the same required claim with a role/instance-preferred source or exact required target and cannot independently contribute to the requested task.

`STALE` and `LOWER_AUTHORITY` may co-occur when both independently apply. No artificial reason may be invented to force non-selection.

## 20. CONFLICT_SERIALIZATION

Conflict **existence** is independent of conflict **terminality**.

1. After universal selection, Router evaluates selected `AVAILABLE` source units for real unresolved material conflicts relevant to current intent.
2. `unresolved_conflict=true` whenever such a conflict exists in selected context, regardless of whether terminal action is `SURFACE_CONFLICT`, `RETRIEVE_CONTEXT`, or `ASK_USER`.
3. When `unresolved_conflict=true`, `conflict_source_refs` contains every selected source ref participating in the unresolved material conflict. Membership is exact; order is non-semantic.
4. When no such selected conflict exists, `unresolved_conflict=false` and `conflict_source_refs=[]`.
5. `action=SURFACE_CONFLICT` requires `unresolved_conflict=true` **and** no higher missing-context gate.
6. `unresolved_conflict=true` does not imply `action=SURFACE_CONFLICT`; a higher missing gate may own the terminal action.
7. A higher missing gate defers conflict **terminal handling**, not conflict truth. The conflict remains visible for downstream reasoning and is re-evaluated after the missing gate changes state.
8. Excluded sources do not appear in `conflict_source_refs`; if authority/currentness rules resolve a disagreement by excluding one source, that disagreement is not serialized as an unresolved selected conflict.
9. Router never silently merges conflict claims into a synthetic fact.

## 21. DETERMINISTIC_EMISSION_RULES

### Evaluation sequence

1. parse governing intent and task scope;
2. classify semantic requirements and whether they require current truth/history/comparison;
3. inspect `source_target` on all candidates and readable `source_unit.claims` only on `AVAILABLE` items;
4. determine materially required non-`AVAILABLE` sources;
5. compute dominant missing state;
6. partition all `AVAILABLE` items through the universal selection/exclusion rules, including equal-eligible all-select;
7. compute unresolved conflict truth across selected sources;
8. choose one terminal action through Section 18 precedence;
9. emit exact runtime reason membership;
10. serialize explicit empty lists/states.

### Least-sufficient supplemental reason

`LEAST_SUFFICIENT_CONTEXT` is emitted iff:

- `action=USE_CONTEXT`; and
- at least one `AVAILABLE` source is excluded with `IRRELEVANT`.

It is not emitted merely because sources are excluded for project boundary, staleness, lower authority, or because a non-USE action carries partial context.

### Primary runtime reason

Exactly one primary reason is emitted:

- `USE_CONTEXT` + no selected sources -> `SELF_CONTAINED_TASK`;
- `USE_CONTEXT` + selected sources -> `AVAILABLE_CONTEXT_SUFFICIENT`;
- `SURFACE_CONFLICT` -> `UNRESOLVED_CONTRADICTION`;
- `ASK_USER + INACCESSIBLE` -> `REQUIRED_CONTEXT_INACCESSIBLE`;
- `ASK_USER + UNRESOLVABLE_WITH_AVAILABLE_SOURCES` -> `USER_INPUT_REQUIRED`;
- `RETRIEVE_CONTEXT` with any required `PROJECT_CANON` or `PROJECT_EVIDENCE` -> `PROJECT_CONTEXT_REQUIRED`;
- otherwise `RETRIEVE_CONTEXT` with required `PERSONAL_CONTINUITY` -> `PERSONAL_CONTINUITY_REQUIRED`;
- otherwise `RETRIEVE_CONTEXT` with required `EXTERNAL_CONTEXT` -> `EXTERNAL_CONTEXT_REQUIRED`.

For multi-domain `RETRIEVE_CONTEXT`, primary domain precedence is:

`PROJECT_CONTEXT_REQUIRED > PERSONAL_CONTINUITY_REQUIRED > EXTERNAL_CONTEXT_REQUIRED`.

### Supplemental retrieval-domain reasons

In multi-domain `RETRIEVE_CONTEXT`, each other applicable retrieval-domain reason not chosen as primary is emitted as supplemental. No retrieval-domain supplemental reasons are emitted for `ASK_USER`; its primary reason is determined by dominant missing state. Exclusion reasons are never copied into runtime reason codes.

### Normalization

Output list order is non-semantic; semantic membership is exact; a harness compares normalized membership and scalar equality; empty lists remain explicit.

## 22. RUNTIME_REASON_CODES

The runtime reason vocabulary is exactly:

```text
AVAILABLE_CONTEXT_SUFFICIENT
SELF_CONTAINED_TASK
LEAST_SUFFICIENT_CONTEXT
PROJECT_CONTEXT_REQUIRED
PERSONAL_CONTINUITY_REQUIRED
EXTERNAL_CONTEXT_REQUIRED
UNRESOLVED_CONTRADICTION
USER_INPUT_REQUIRED
REQUIRED_CONTEXT_INACCESSIBLE
```

Meanings:

- `AVAILABLE_CONTEXT_SUFFICIENT` — selected available context is sufficient and no higher gate remains.
- `SELF_CONTAINED_TASK` — governing task input alone is sufficient.
- `LEAST_SUFFICIENT_CONTEXT` — irrelevant available context was excluded from an otherwise sufficient use-context result.
- `PROJECT_CONTEXT_REQUIRED` — materially required project canon/evidence is retrievable but not available; it does not universally claim the missing item outranks every selected source.
- `PERSONAL_CONTINUITY_REQUIRED` — required continuity is retrievable but not available.
- `EXTERNAL_CONTEXT_REQUIRED` — required external context is retrievable but not available. Currentness, when required, is represented by task semantics plus freshness metadata rather than this domain reason name.
- `UNRESOLVED_CONTRADICTION` — selected available sources materially conflict and no higher missing gate owns the terminal action.
- `USER_INPUT_REQUIRED` — at least one required target is unavailable and cannot be established through the declared context envelope.
- `REQUIRED_CONTEXT_INACCESSIBLE` — no required target is unavailable, but at least one exact required target is inaccessible.

`HIGHER_AUTHORITY_CONTEXT_REQUIRED` and `EXTERNAL_CURRENT_CONTEXT_REQUIRED` are invalid R5 runtime outputs.

## 23. CONTRACT_INVARIANTS

### Structural

1. Exactly one terminal action is emitted.
2. Exactly four terminal action values exist.
3. Exactly four role-only source classes exist.
4. Current user intent is governing input only.
5. Kernel is governing plane only.
6. Inference is non-routable.
7. No source-class name encodes provenance, availability, freshness, verification, or canon-instance role.
8. No tool, mode, execution-authority, permission, execution, canon-mutation, or numeric context-budget field exists.

### Target / binding / metadata

9. Every source item has one unique opaque `source_ref`.
10. Every source item has a non-empty `source_target.description`.
11. `source_target` carries semantic target identity only; it carries no authority/freshness/verification and never proves content access.
12. Every output ref exists in input; Router never invents target refs.
13. Every `AVAILABLE` item has readable non-empty claims.
14. A non-`AVAILABLE` item may have `source_unit: null` without losing semantic target identity.
15. One source item is one homogeneous routing-relevant claim set.
16. Selected metadata exactly preserves input metadata.
17. Verification and canon-instance role remain upstream-owned/read-only.

### Currentness / authority

18. Explicit `STALE` never satisfies a materially current-truth requirement.
19. Source role cannot erase explicit stale ineligibility.
20. Stale material may be selected for requested history/comparison.
21. `UNKNOWN` freshness is not silently promoted to `CURRENT`.
22. If current truth is required and no eligible current source is available, an exact non-`AVAILABLE` target must already exist in input.
23. Verification validates claims, not source roles.
24. `PERSONAL_CONTINUITY` and `EXTERNAL_CONTEXT` never cross-promote into project truth through verification/currentness.
25. `ROOT_OF_TRUST > DEPLOYED_COPY` never invents access.
26. Neither `source_ref` spelling nor input order is an authority/tie-break rule.

### Universal selection / exclusion

27. Only `AVAILABLE` items may be selected.
28. Every `AVAILABLE` item is exactly one of selected or excluded for every action.
29. No non-`AVAILABLE` item appears in exclusions.
30. No item is both selected and excluded.
31. Every exclusion has at least one truthful applicable reason.
32. An available item is never excluded solely because terminal action is retrieval or clarification.
33. Partial selected context may coexist with `RETRIEVE_CONTEXT` or `ASK_USER`.
34. If multiple available sources are equally eligible, materially relevant, non-conflicting, and no exclusion reason applies, all are selected.
35. No `REDUNDANT` exclusion reason exists in R5.
36. No artificial exclusion reason is permitted.

### Missing / terminal totality

37. `missing_context.required_sources` contains all and only materially required non-`AVAILABLE` source items whenever state is non-`NONE`.
38. Missing dominance is `UNAVAILABLE > INACCESSIBLE > RETRIEVABLE`.
39. `UNAVAILABLE` dominant -> `ASK_USER / UNRESOLVABLE_WITH_AVAILABLE_SOURCES`.
40. Else `INACCESSIBLE` dominant -> `ASK_USER / INACCESSIBLE`.
41. Else `RETRIEVABLE` present -> `RETRIEVE_CONTEXT / REQUIRED`.
42. Else selected unresolved conflict -> `SURFACE_CONFLICT / NONE`.
43. Else -> `USE_CONTEXT / NONE`.
44. A missing gate dominates conflict only as terminal action.

### Conflict truthfulness

45. `unresolved_conflict=true` iff selected available context contains at least one real unresolved material conflict after eligibility/authority rules.
46. When conflict is true, `conflict_source_refs` contains all selected participant refs; otherwise it is empty.
47. `action=SURFACE_CONFLICT` -> `unresolved_conflict=true`.
48. `unresolved_conflict=true` plus no higher missing gate -> `action=SURFACE_CONFLICT`.
49. `unresolved_conflict=true` may coexist with `RETRIEVE_CONTEXT` or `ASK_USER` when a higher missing gate wins.
50. No higher gate may serialize an existing selected conflict as false.

### Reason semantics

51. Exactly one primary runtime reason exists.
52. Missing project canon/evidence retrieval uses `PROJECT_CONTEXT_REQUIRED`.
53. Missing external retrieval uses `EXTERNAL_CONTEXT_REQUIRED`.
54. `HIGHER_AUTHORITY_CONTEXT_REQUIRED` and `EXTERNAL_CURRENT_CONTEXT_REQUIRED` are invalid R5 outputs.
55. `LEAST_SUFFICIENT_CONTEXT` follows its exact iff rule.
56. Tool/mode/execution/canon boundaries are structural assertions, not runtime reason codes.

## 24. HARD_FAIL_ASSERTION_CATALOG

The catalog is conformance-only; it does not add runtime behavior. Every ID referenced by the 20 fixtures is defined here, and no unreferenced catalog ID is retained.

- `HF_ALL_REQUIRED_NONAVAILABLE_REFS_SERIALIZED` — When missing state is non-`NONE`, `required_sources` contains all and only materially required non-`AVAILABLE` source refs, including lower-dominance dependencies.
- `HF_CANON_INSTANCE_ROLE_INPUT_OWNED` — `canon_instance_role` is upstream-owned/read-only, meaningful only for `PROJECT_CANON`, and never inferred from identifiers, names, paths, or content wording.
- `HF_CONFLICT_MAPPING` — `unresolved_conflict` and `conflict_source_refs` truthfully represent all selected source refs participating in a real unresolved material conflict; `SURFACE_CONFLICT` is used only when no higher missing gate wins.
- `HF_CONFLICT_VISIBLE_WHEN_GATE_DOMINATED` — A higher missing gate does not suppress conflict truth: if selected `AVAILABLE` sources materially conflict, `unresolved_conflict=true` and exact participant refs remain serialized under `RETRIEVE_CONTEXT` or `ASK_USER`.
- `HF_CURRENTNESS_ELIGIBILITY` — For a materially current-truth requirement, only freshness-eligible sources may satisfy completion; explicit `STALE` cannot satisfy it and `UNKNOWN` is not silently promoted to `CURRENT`.
- `HF_DOMINANT_MISSING_STATE` — `missing_context.state` equals the strongest state implied by materially required non-`AVAILABLE` inputs: `UNRESOLVABLE_WITH_AVAILABLE_SOURCES > INACCESSIBLE > REQUIRED > NONE`.
- `HF_EQUAL_ELIGIBLE_ALL_SELECTED` — All `AVAILABLE` sources that are equally eligible, materially relevant, non-conflicting, and lack a truthful exclusion reason are selected; input order and `source_ref` spelling are not tie-breakers.
- `HF_EXACT_ROUTING_RESULT_MATCH` — After order normalization, the emitted `routing_result` equals the fixture’s complete expected `routing_result` in every field and membership.
- `HF_EXCLUSION_MEMBERSHIP_EXACT` — Every `AVAILABLE` source is exactly selected or excluded, no non-`AVAILABLE` source is excluded, no overlap exists, and exclusion reasons match the frozen rules and fixture expectation.
- `HF_LEAST_SUFFICIENT_RULE` — `LEAST_SUFFICIENT_CONTEXT` appears iff `action=USE_CONTEXT` and at least one `AVAILABLE` source is excluded as `IRRELEVANT`.
- `HF_MISSING_MAPPING` — Terminal action, `missing_context.state`, and exact `required_sources` membership follow the frozen non-available dominance and all-required serialization rules.
- `HF_MIXED_MISSING_GATE_PRECEDENCE` — Terminal precedence is required `UNAVAILABLE` > required `INACCESSIBLE` > required `RETRIEVABLE` > unresolved selected conflict > `USE_CONTEXT`.
- `HF_NO_AUTHORITY_FIELD` — The result contains no semantic execution-authority or platform-permission state.
- `HF_NO_CANON_MUTATION` — Router does not promote, mutate, relabel, or fork canon; candidates retain their supplied role.
- `HF_NO_EXECUTION_FIELD` — The result contains no external-state execution action, payload, send/publish/pause/delete/deploy semantics, or equivalent mutation field.
- `HF_NO_INFERENCE_SOURCE` — `INFERENCE` never appears as a source class or factual substitute for required missing context.
- `HF_NO_KERNEL_SOURCE` — Kernel governing context never appears in routable input/output source fields and is not treated as project evidence.
- `HF_NO_LOCAL_ACCESS_INVENTION` — An inaccessible local/root-of-trust canon target is never described as read, retrieved, checked, equal to another copy, or otherwise accessed.
- `HF_NO_MODE_FIELD` — The result contains no reasoning-mode/effort selection or mode action/field.
- `HF_NO_ROLE_PROMOTION` — Freshness, verification, provenance, or availability never changes a source’s role/class; continuity or external context is not promoted into project-truth roles.
- `HF_NO_ROUTABLE_CURRENT_USER_INTENT` — `CURRENT_USER_INTENT` is never serialized as a routable source, selected source, exclusion, conflict ref, or required source.
- `HF_NO_SILENT_CONFLICT_MERGE` — Materially conflicting eligible sources are not silently blended, synthesized, or arbitrarily tie-broken without a frozen precedence basis.
- `HF_NO_TOOL_FIELD` — The routing result contains no concrete tool/connector selection, invocation, retrieval implementation, or tool-specific field.
- `HF_NO_UNNECESSARY_CONTEXT` — The Router does not retrieve or select context that is irrelevant to a self-contained/sufficient task; equal eligible materially relevant sources are not considered unnecessary.
- `HF_NO_VERIFICATION_SYNTHESIS` — Router never changes or invents upstream verification state and never treats retrieval/availability/freshness as proof of `VERIFIED`.
- `HF_PARTIAL_SELECTION_WITH_RETRIEVAL` — `RETRIEVE_CONTEXT` or `ASK_USER` preserves every `AVAILABLE` source that satisfies the universal selection rule instead of dropping it because the terminal action is non-USE.
- `HF_PROJECT_CONTEXT_REASON_TRUTHFUL` — Retrieval of materially required `PROJECT_CANON` or `PROJECT_EVIDENCE` uses `PROJECT_CONTEXT_REQUIRED` without falsely asserting universal higher-authority status.
- `HF_PROJECT_EVIDENCE_REASON_IS_PROJECT_CONTEXT_REQUIRED` — A required retrievable `PROJECT_EVIDENCE` target is represented by runtime reason `PROJECT_CONTEXT_REQUIRED`.
- `HF_PROVENANCE_NOT_AVAILABILITY` — Provenance stays within `USER_STATED|RETRIEVED|REMEMBERED|UNKNOWN`; availability is represented only by the separate availability field.
- `HF_REASON_MEMBERSHIP_EXACT` — Exactly one primary runtime reason and the exact supplemental reason set required by Sections 21–22 are emitted; no extra or deprecated reason is present.
- `HF_RETRIEVAL_GATE_PRECEDES_AVAILABLE_CONFLICT` — A materially required `RETRIEVABLE` source keeps terminal action `RETRIEVE_CONTEXT` even when selected `AVAILABLE` sources also contain an unresolved material conflict.
- `HF_SCOPE_ISOLATION` — A source outside governing task scope is excluded with `PROJECT_BOUNDARY` unless the current intent explicitly requires cross-scope comparison.
- `HF_SELECTED_METADATA_PRESERVED` — Every selected source copies `source_class`, `provenance`, `freshness`, `upstream_verification`, and `canon_instance_role` exactly from its input item.
- `HF_SELECTED_ONLY_AVAILABLE` — Every `selected_sources` ref binds to an input item with `availability=AVAILABLE`.
- `HF_SINGLE_TERMINAL_ACTION` — Exactly one `action` is emitted and it is one of the four frozen terminal actions.
- `HF_SOURCE_TARGET_REQUIRED` — Every source item has a non-empty `source_target.description`; non-`AVAILABLE` target matching relies on this descriptor rather than unavailable content or `source_ref` text.
- `HF_STALE_CANON_CANNOT_SATISFY_CURRENT_TRUTH` — A `PROJECT_CANON` item with `freshness=STALE` cannot satisfy a current-truth requirement merely because it is canon.

## 25. UPDATED_20_CASE_MACHINE_CHECKABLE_EVAL_SUITE

The suite remains exactly 20 IDs (`CR-001` … `CR-020`) and preserves their categories. R5 modifies only the fields/expectations needed to prove the five closure properties. Every fixture is a complete machine-checkable YAML object.

Notable closure coverage: `source_target` is present on every source item; non-`AVAILABLE` cases explicitly rely on it; CR-017 contains two equal eligible non-conflicting sources and requires both selected; CR-020 keeps a real available conflict visible while `RETRIEVE_CONTEXT` remains the terminal action; CR-008 and CR-013 use `EXTERNAL_CONTEXT_REQUIRED`.

### CASE CR-001 — Fresh verified project state beats stale project context

```yaml
id: CR-001
title: Fresh verified project state beats stale project context
routing_input:
  current_user_intent:
    instruction: State the current Demo service interface approval status.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:01
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: STALE
    upstream_verification: UNKNOWN
    canon_instance_role: STANDARD
    source_target:
      description: Demo service interface approval status claim
    source_unit:
      claims:
      - An older sample record says the interface is approved.
  - source_ref: ref:02
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: VERIFIED
    canon_instance_role: null
    source_target:
      description: Demo service interface approval status claim
    source_unit:
      claims:
      - The current sample review says interface approval is pending.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:02
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: VERIFIED
      canon_instance_role: null
    exclusions:
    - source_ref: ref:01
      source_class: PROJECT_CANON
      reasons:
      - STALE
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_CURRENTNESS_ELIGIBILITY
- HF_STALE_CANON_CANNOT_SATISFY_CURRENT_TRUTH
- HF_SELECTED_METADATA_PRESERVED
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-002 — Verified continuity does not cross-promote into project truth

```yaml
id: CR-002
title: Verified continuity does not cross-promote into project truth
routing_input:
  current_user_intent:
    instruction: Use the canonical release branch for project truth.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:03
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: STANDARD
    source_target:
      description: Canonical release-branch claim
    source_unit:
      claims:
      - The designated sample release branch is branch-alpha.
  - source_ref: ref:04
    source_class: PERSONAL_CONTINUITY
    scope_ref: scope:demo-project
    provenance: REMEMBERED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: VERIFIED
    canon_instance_role: null
    source_target:
      description: Remembered release-branch claim
    source_unit:
      claims:
      - The prior sample release branch is branch-previous.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:03
      source_class: PROJECT_CANON
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: STANDARD
    exclusions:
    - source_ref: ref:04
      source_class: PERSONAL_CONTINUITY
      reasons:
      - LOWER_AUTHORITY
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_NO_ROLE_PROMOTION
- HF_SELECTED_METADATA_PRESERVED
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-003 — Project evidence is used when canon is silent

```yaml
id: CR-003
title: Project evidence is used when canon is silent
routing_input:
  current_user_intent:
    instruction: What did the latest sandbox verification report record?
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:05
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: sandbox verification-result claim
    source_unit:
      claims:
      - The latest sandbox verification report records DEPLOYMENT_CHECK = PASSED.
  - source_ref: ref:06
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: STANDARD
    source_target:
      description: Project governance-rule claim set
    source_unit:
      claims:
      - Project canon defines governance rules but contains no sandbox verification-result claim.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:05
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions:
    - source_ref: ref:06
      source_class: PROJECT_CANON
      reasons:
      - IRRELEVANT
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental:
      - LEAST_SUFFICIENT_CONTEXT
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SELECTED_METADATA_PRESERVED
- HF_NO_VERIFICATION_SYNTHESIS
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_LEAST_SUFFICIENT_RULE
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-004 — Remembered provenance stays remembered

```yaml
id: CR-004
title: Remembered provenance stays remembered
routing_input:
  current_user_intent:
    instruction: What synthetic profile preference is shown?
    scope_ref: NONE
  source_items:
  - source_ref: ref:07
    source_class: PERSONAL_CONTINUITY
    scope_ref: NONE
    provenance: REMEMBERED
    availability: AVAILABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Previously known user-preference claim
    source_unit:
      claims:
      - 'Synthetic profile preference: concise reports are preferred.'
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:07
      source_class: PERSONAL_CONTINUITY
      provenance: REMEMBERED
      freshness: UNKNOWN
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions: []
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SELECTED_METADATA_PRESERVED
- HF_PROVENANCE_NOT_AVAILABILITY
- HF_NO_VERIFICATION_SYNTHESIS
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-005 — Retrieved is not verified

```yaml
id: CR-005
title: Retrieved is not verified
routing_input:
  current_user_intent:
    instruction: Use the retrieved project evidence.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:08
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Context Router implementation-status claim
    source_unit:
      claims:
      - Retrieved sample evidence states that implementation has not started.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:08
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions: []
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SELECTED_METADATA_PRESERVED
- HF_NO_VERIFICATION_SYNTHESIS
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-006 — Self-contained task requires no routable source

```yaml
id: CR-006
title: Self-contained task requires no routable source
routing_input:
  current_user_intent:
    instruction: 'Rewrite this fully supplied sentence: Context routing must stay narrow.'
    scope_ref: NONE
  source_items: []
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources: []
    exclusions: []
    reason_codes:
      primary: SELF_CONTAINED_TASK
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_NO_ROUTABLE_CURRENT_USER_INTENT
- HF_NO_UNNECESSARY_CONTEXT
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-007 — Synthetic personalization requires profile context

```yaml
id: CR-007
title: Synthetic personalization requires profile context
routing_input:
  current_user_intent:
    instruction: Recommend something using the synthetic profile preference.
    scope_ref: NONE
  source_items:
  - source_ref: ref:07-profile
    source_class: PERSONAL_CONTINUITY
    scope_ref: NONE
    provenance: UNKNOWN
    availability: RETRIEVABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Established long-term preference profile for personalized recommendation
    source_unit: null
expected:
  routing_result:
    action: RETRIEVE_CONTEXT
    selected_sources: []
    exclusions: []
    reason_codes:
      primary: PERSONAL_CONTINUITY_REQUIRED
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: REQUIRED
      required_sources:
      - source_ref: ref:07-profile
        source_class: PERSONAL_CONTINUITY
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_SELECTED_ONLY_AVAILABLE
- HF_MISSING_MAPPING
- HF_NO_INFERENCE_SOURCE
- HF_NO_TOOL_FIELD
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-008 — Current external fact requires external context

```yaml
id: CR-008
title: Current external fact requires external context
routing_input:
  current_user_intent:
    instruction: State whether the external service is currently available now.
    scope_ref: NONE
  source_items:
  - source_ref: ref:09
    source_class: EXTERNAL_CONTEXT
    scope_ref: NONE
    provenance: UNKNOWN
    availability: RETRIEVABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Availability state of the external service
    source_unit: null
expected:
  routing_result:
    action: RETRIEVE_CONTEXT
    selected_sources: []
    exclusions: []
    reason_codes:
      primary: EXTERNAL_CONTEXT_REQUIRED
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: REQUIRED
      required_sources:
      - source_ref: ref:09
        source_class: EXTERNAL_CONTEXT
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_MISSING_MAPPING
- HF_NO_TOOL_FIELD
- HF_NO_VERIFICATION_SYNTHESIS
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-009 — Cross-project contamination is rejected

```yaml
id: CR-009
title: Cross-project contamination is rejected
routing_input:
  current_user_intent:
    instruction: State the active sample-project task.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:10
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Sample-project task claim
    source_unit:
      claims:
      - The demo contract revision is the active sample task.
  - source_ref: ref:11
    source_class: PERSONAL_CONTINUITY
    scope_ref: scope:real-estate
    provenance: REMEMBERED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Real-estate project phase claim
    source_unit:
      claims:
      - The catalog sample project is in its domain-model phase.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:10
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions:
    - source_ref: ref:11
      source_class: PERSONAL_CONTINUITY
      reasons:
      - PROJECT_BOUNDARY
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SCOPE_ISOLATION
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-010 — Equal-authority material conflict is surfaced

```yaml
id: CR-010
title: Equal-authority material conflict is surfaced
routing_input:
  current_user_intent:
    instruction: State whether the Router interface is freeze-ready.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:12A
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Router interface freeze-readiness claim
    source_unit:
      claims:
      - The Router interface is freeze-ready.
  - source_ref: ref:12B
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Router interface freeze-readiness claim
    source_unit:
      claims:
      - The Router interface is not freeze-ready.
expected:
  routing_result:
    action: SURFACE_CONFLICT
    selected_sources:
    - source_ref: ref:12A
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    - source_ref: ref:12B
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions: []
    reason_codes:
      primary: UNRESOLVED_CONTRADICTION
      supplemental: []
    unresolved_conflict: true
    conflict_source_refs:
    - ref:12A
    - ref:12B
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_CONFLICT_MAPPING
- HF_NO_SILENT_CONFLICT_MERGE
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-011 — Higher-authority project canon is missing but retrievable

```yaml
id: CR-011
title: Higher-authority project canon is missing but retrievable
routing_input:
  current_user_intent:
    instruction: Use the current canonical release branch.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:13
    source_class: PERSONAL_CONTINUITY
    scope_ref: scope:demo-project
    provenance: REMEMBERED
    availability: AVAILABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Remembered canonical release-branch claim
    source_unit:
      claims:
      - The prior sample canonical branch is branch-previous.
  - source_ref: ref:14
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: UNKNOWN
    availability: RETRIEVABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: STANDARD
    source_target:
      description: Canonical release-branch claim
    source_unit: null
expected:
  routing_result:
    action: RETRIEVE_CONTEXT
    selected_sources: []
    exclusions:
    - source_ref: ref:13
      source_class: PERSONAL_CONTINUITY
      reasons:
      - LOWER_AUTHORITY
    reason_codes:
      primary: PROJECT_CONTEXT_REQUIRED
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: REQUIRED
      required_sources:
      - source_ref: ref:14
        source_class: PROJECT_CANON
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_PROJECT_CONTEXT_REASON_TRUTHFUL
- HF_MISSING_MAPPING
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_NO_TOOL_FIELD
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-012 — Kernel is governing plane, not project evidence

```yaml
id: CR-012
title: Kernel is governing plane, not project evidence
routing_input:
  current_user_intent:
    instruction: State the current Context Router project status.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:15
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Context Router project-status claim
    source_unit:
      claims:
      - The demo system remains a contract/evaluation candidate and implementation is NOT_STARTED.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:15
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions: []
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_NO_KERNEL_SOURCE
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-013 — Tool Router boundary remains structural

```yaml
id: CR-013
title: Tool Router boundary remains structural
routing_input:
  current_user_intent:
    instruction: Check the current external fact.
    scope_ref: NONE
  source_items:
  - source_ref: ref:18
    source_class: EXTERNAL_CONTEXT
    scope_ref: NONE
    provenance: UNKNOWN
    availability: RETRIEVABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: External fact requested by the task
    source_unit: null
expected:
  routing_result:
    action: RETRIEVE_CONTEXT
    selected_sources: []
    exclusions: []
    reason_codes:
      primary: EXTERNAL_CONTEXT_REQUIRED
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: REQUIRED
      required_sources:
      - source_ref: ref:18
        source_class: EXTERNAL_CONTEXT
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_NO_TOOL_FIELD
- HF_MISSING_MAPPING
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-014 — Mode Engine boundary remains structural

```yaml
id: CR-014
title: Mode Engine boundary remains structural
routing_input:
  current_user_intent:
    instruction: Compare the governing canon rule with the current static-review evidence.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:19
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: STANDARD
    source_target:
      description: Kernel governing-plane separation canon rule
    source_unit:
      claims:
      - Canon requires Kernel governing-plane separation.
  - source_ref: ref:20
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: UNKNOWN
    availability: RETRIEVABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Static-review evidence needed for the requested comparison
    source_unit: null
expected:
  routing_result:
    action: RETRIEVE_CONTEXT
    selected_sources:
    - source_ref: ref:19
      source_class: PROJECT_CANON
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: STANDARD
    exclusions: []
    reason_codes:
      primary: PROJECT_CONTEXT_REQUIRED
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: REQUIRED
      required_sources:
      - source_ref: ref:20
        source_class: PROJECT_EVIDENCE
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_PARTIAL_SELECTION_WITH_RETRIEVAL
- HF_PROJECT_EVIDENCE_REASON_IS_PROJECT_CONTEXT_REQUIRED
- HF_NO_MODE_FIELD
- HF_MISSING_MAPPING
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-015 — Context sufficiency does not create execution authority

```yaml
id: CR-015
title: Context sufficiency does not create execution authority
routing_input:
  current_user_intent:
    instruction: Use the current decision-target evidence for analysis only.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:21
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: VERIFIED
    canon_instance_role: null
    source_target:
      description: Decision-target evidence claim
    source_unit:
      claims:
      - The current verified decision target is Target-Z.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:21
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: VERIFIED
      canon_instance_role: null
    exclusions: []
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_NO_AUTHORITY_FIELD
- HF_NO_EXECUTION_FIELD
- HF_SELECTED_METADATA_PRESERVED
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-016 — Candidate remains non-canon

```yaml
id: CR-016
title: Candidate remains non-canon
routing_input:
  current_user_intent:
    instruction: Compare the candidate proposal with current canon; do not promote it.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:22
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: STANDARD
    source_target:
      description: Current Context Router canon/design-rule claim
    source_unit:
      claims:
      - Current canon keeps Context Router narrow and non-executing.
  - source_ref: ref:23
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Candidate Context Router extension proposal
    source_unit:
      claims:
      - Candidate proposal suggests an optional future extension but is not canon.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:22
      source_class: PROJECT_CANON
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: STANDARD
    - source_ref: ref:23
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions: []
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_NO_CANON_MUTATION
- HF_NO_ROLE_PROMOTION
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-017 — Least-sufficient source set

```yaml
id: CR-017
title: Least-sufficient source set
routing_input:
  current_user_intent:
    instruction: What is the sandbox deployment status?
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:24
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: VERIFIED
    canon_instance_role: null
    source_target:
      description: sandbox deployment-status claim
    source_unit:
      claims:
      - The sandbox deployment state is PASSED.
  - source_ref: ref:24B
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: VERIFIED
    canon_instance_role: null
    source_target:
      description: sandbox deployment-status claim
    source_unit:
      claims:
      - The controlled sandbox deployment status is PASSED.
  - source_ref: ref:25
    source_class: PERSONAL_CONTINUITY
    scope_ref: NONE
    provenance: REMEMBERED
    availability: AVAILABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Synthetic profile preference claim
    source_unit:
      claims:
      - The synthetic profile prefers short examples.
  - source_ref: ref:26
    source_class: EXTERNAL_CONTEXT
    scope_ref: NONE
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Unrelated external release claim
    source_unit:
      claims:
      - An unrelated external service published a new release.
expected:
  routing_result:
    action: USE_CONTEXT
    selected_sources:
    - source_ref: ref:24
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: VERIFIED
      canon_instance_role: null
    - source_ref: ref:24B
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: VERIFIED
      canon_instance_role: null
    exclusions:
    - source_ref: ref:25
      source_class: PERSONAL_CONTINUITY
      reasons:
      - IRRELEVANT
    - source_ref: ref:26
      source_class: EXTERNAL_CONTEXT
      reasons:
      - IRRELEVANT
    reason_codes:
      primary: AVAILABLE_CONTEXT_SUFFICIENT
      supplemental:
      - LEAST_SUFFICIENT_CONTEXT
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: NONE
      required_sources: []
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_EQUAL_ELIGIBLE_ALL_SELECTED
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_LEAST_SUFFICIENT_RULE
- HF_REASON_MEMBERSHIP_EXACT
- HF_NO_UNNECESSARY_CONTEXT
```


### CASE CR-018 — Unknown stays unknown; inference is not routable

```yaml
id: CR-018
title: Unknown stays unknown; inference is not routable
routing_input:
  current_user_intent:
    instruction: Resolve the required project fact, root-of-trust check, and current external dependency.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:27U
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: UNKNOWN
    availability: UNAVAILABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Required project fact requested by the task
    source_unit: null
  - source_ref: ref:27I
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: UNKNOWN
    availability: INACCESSIBLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: ROOT_OF_TRUST
    source_target:
      description: Local project canon instance required by the task
    source_unit: null
  - source_ref: ref:27R
    source_class: EXTERNAL_CONTEXT
    scope_ref: NONE
    provenance: UNKNOWN
    availability: RETRIEVABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: External dependency requested by the task
    source_unit: null
expected:
  routing_result:
    action: ASK_USER
    selected_sources: []
    exclusions: []
    reason_codes:
      primary: USER_INPUT_REQUIRED
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: UNRESOLVABLE_WITH_AVAILABLE_SOURCES
      required_sources:
      - source_ref: ref:27U
        source_class: PROJECT_EVIDENCE
      - source_ref: ref:27I
        source_class: PROJECT_CANON
      - source_ref: ref:27R
        source_class: EXTERNAL_CONTEXT
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_NO_INFERENCE_SOURCE
- HF_MIXED_MISSING_GATE_PRECEDENCE
- HF_DOMINANT_MISSING_STATE
- HF_ALL_REQUIRED_NONAVAILABLE_REFS_SERIALIZED
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-019 — Required local root-of-trust canon is inaccessible

```yaml
id: CR-019
title: Required local root-of-trust canon is inaccessible
routing_input:
  current_user_intent:
    instruction: Validate the decision against the local root-of-trust project canon; the deployed copy is insufficient.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:28
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: DEPLOYED_COPY
    source_target:
      description: Deployed project-canon instance available in the sandbox runtime
    source_unit:
      claims:
      - This is the deployed project-canon copy available in the sandbox runtime.
  - source_ref: ref:29
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: UNKNOWN
    availability: INACCESSIBLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: ROOT_OF_TRUST
    source_target:
      description: Local project-canon instance requested for comparison
    source_unit: null
expected:
  routing_result:
    action: ASK_USER
    selected_sources: []
    exclusions:
    - source_ref: ref:28
      source_class: PROJECT_CANON
      reasons:
      - LOWER_AUTHORITY
    reason_codes:
      primary: REQUIRED_CONTEXT_INACCESSIBLE
      supplemental: []
    unresolved_conflict: false
    conflict_source_refs: []
    missing_context:
      state: INACCESSIBLE
      required_sources:
      - source_ref: ref:29
        source_class: PROJECT_CANON
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_CANON_INSTANCE_ROLE_INPUT_OWNED
- HF_NO_LOCAL_ACCESS_INVENTION
- HF_MISSING_MAPPING
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_REASON_MEMBERSHIP_EXACT
```


### CASE CR-020 — Available context plus exclusion remains one action

```yaml
id: CR-020
title: Available context plus exclusion remains one action
routing_input:
  current_user_intent:
    instruction: Resolve the current canonical release target; available project evidence conflicts.
    scope_ref: scope:demo-project
  source_items:
  - source_ref: ref:30A
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Canonical release-target claim carried by available project evidence
    source_unit:
      claims:
      - Available evidence A says branch-alpha.
  - source_ref: ref:30B
    source_class: PROJECT_EVIDENCE
    scope_ref: scope:demo-project
    provenance: RETRIEVED
    availability: AVAILABLE
    freshness: CURRENT
    upstream_verification: UNKNOWN
    canon_instance_role: null
    source_target:
      description: Canonical release-target claim carried by available project evidence
    source_unit:
      claims:
      - Available evidence B says branch-previous.
  - source_ref: ref:31
    source_class: PROJECT_CANON
    scope_ref: scope:demo-project
    provenance: UNKNOWN
    availability: RETRIEVABLE
    freshness: UNKNOWN
    upstream_verification: UNKNOWN
    canon_instance_role: STANDARD
    source_target:
      description: Canonical release-target claim from project canon
    source_unit: null
expected:
  routing_result:
    action: RETRIEVE_CONTEXT
    selected_sources:
    - source_ref: ref:30A
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    - source_ref: ref:30B
      source_class: PROJECT_EVIDENCE
      provenance: RETRIEVED
      freshness: CURRENT
      upstream_verification: UNKNOWN
      canon_instance_role: null
    exclusions: []
    reason_codes:
      primary: PROJECT_CONTEXT_REQUIRED
      supplemental: []
    unresolved_conflict: true
    conflict_source_refs:
    - ref:30A
    - ref:30B
    missing_context:
      state: REQUIRED
      required_sources:
      - source_ref: ref:31
        source_class: PROJECT_CANON
hard_fail_assertions:
- HF_EXACT_ROUTING_RESULT_MATCH
- HF_SOURCE_TARGET_REQUIRED
- HF_SINGLE_TERMINAL_ACTION
- HF_RETRIEVAL_GATE_PRECEDES_AVAILABLE_CONFLICT
- HF_CONFLICT_VISIBLE_WHEN_GATE_DOMINATED
- HF_EXCLUSION_MEMBERSHIP_EXACT
- HF_REASON_MEMBERSHIP_EXACT
```

## 26. PROMOTION_GATE

R5 is **not** promoted and does not freeze the interface by itself. Implementation remains blocked until interface freeze.

Run exactly this seven-point R5 freeze exit check:

1. all 20 fixtures parse and match the frozen input/output schema and exact expected-result rules;
2. every `HF_*` used by fixtures is defined in Section 24, and the catalog contains no unused assertion IDs;
3. every non-`AVAILABLE` target is semantically matchable through `source_target.description` without reading unavailable content or parsing `source_ref`;
4. conflict truth remains visible when a higher missing gate owns the terminal action;
5. equivalent/equal eligible sources have one deterministic all-select treatment without arbitrary tie-breaks or `REDUNDANT`;
6. external retrieval uses role-true `EXTERNAL_CONTEXT_REQUIRED` everywhere;
7. no ownership expands into Kernel modification, Verification, Tool Router, Mode Engine, execution authority, execution, canon mutation, or new architectural layers.

If all seven pass and no direct contradiction exists, the next review may set `INTERFACE_FREEZE = PASS`. Do not broaden that review into speculative v0.2 features.

## 27. OPEN_QUESTIONS

No known open question in this section blocks the R5 closure contract itself. The remaining questions are intentionally downstream/outside v0.1 interface ownership:

1. Concrete Tool Router handoff representation for `RETRIEVE_CONTEXT` after interface freeze.
2. Concrete Verification handoff/receipt representation for upstream verification metadata.
3. Concrete implementation language/runtime and internal algorithm after interface freeze.
4. Any numeric context/source/token budget only if future evidence supplies a justified resource model.

New unobserved requirements belong to v0.2+ rather than reopening the R5 freeze exit check.

## 28. REVISION_VERDICT

R5 is the smallest closure revision of R4 that resolves the five R4 freeze blockers without redesigning Router scope:

- every source now has a task-readable `source_target`, so non-`AVAILABLE` target identity is deterministic without pretending content was accessed;
- terminal missing-gate precedence is preserved while unresolved selected conflicts remain truthfully serialized under `RETRIEVE_CONTEXT`/`ASK_USER`;
- equal eligible non-conflicting sources deterministically all-select rather than using opaque IDs/input order or a fabricated redundancy exclusion;
- external retrieval now uses `EXTERNAL_CONTEXT_REQUIRED`, leaving currentness to task semantics and freshness metadata;
- the hard-fail assertion vocabulary is now self-contained and fixture-bound;
- exactly 20 eval IDs/categories remain;
- no Router implementation, Kernel modification, architecture layer, tool/mode ownership, execution authority, execution, or canon promotion occurred.

This artifact deliberately leaves `INTERFACE_FREEZE_STATUS = NOT_YET`; the seven-point R5 freeze exit check is the next and only closure gate.

ROUTER_v0.1_STATUS = CONTRACT_AND_EVAL_CANDIDATE_R5
INTERFACE_FREEZE_STATUS = NOT_YET
IMPLEMENTATION_STATUS = NOT_STARTED
NEXT_RECOMMENDED_ACTION = Run the seven-point R5 freeze exit check; if all pass and no direct contradiction exists, freeze Context Router v0.1 interface.
