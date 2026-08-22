# CCO-Domains Base Conformance Profile — Rationale and Notes

**Companion to:** `CCO-Domains_Base_Conformance_Profile_v0_1.ttl`
**Date:** 2026-08-08 · **Governing decision:** DL-013 (all seven sections)
**Status:** v0.1 — first tested artifact; built against merged w3id.org/cco-domains namespace.

This document carries the rationale, caveats, and scope notes that belong
alongside the normative shapes file but not *in* it. The `.ttl` file is the
normative artifact; this document explains the decisions behind each shape.

---

## How to use the profile

The `.ttl` is a standard SHACL file. Run it with any SHACL 1.0-compliant
processor (pyshacl, TopBraid, etc.) against instance data that uses
CCO-Domains terms. It does NOT require OWL reasoning and is not designed
for Protégé's OWL view — use a SHACL tool, not an OWL editor.

Quick validation with pyshacl:
```
pyshacl -s CCO-Domains_Base_Conformance_Profile_v0_1.ttl your-instance-data.ttl
```

Tested against a real instance (Paul Trevithick's California DMV drivers-license
databook, MeeFoundation/mia-ontologies, commit ca8da1c) on 2026-08-08:
correctly catches one violation (untyped date), no false positives on
designation/carrier/jurisdiction triples.

---

## §2 — Designation pattern

**`cp:DesignationNodeShape`** — A designation node (the thing on the far end
of `designated by`, ont00001879) must carry exactly one `has text value`
(ont00001765) literal. Datatype is unconstrained at the base — domains tighten
(e.g., xsd:date for date identifiers, xsd:string for names). `nodeKind sh:Literal`
is universal: a designation value is always a literal, never an IRI or blank node.

**`cp:DesignatedSubjectShape`** — Every node reached by `designated by` must
satisfy `DesignationNodeShape`. Universal enforcement (not opt-in) because
`designated by` is inherently a designation relation: anything on its range is,
by definition, a designation node. In an open-write user-data store (any external
app can write), this is what lets a reading app trust the shape of every
designation it encounters — not just the ones some domain profile named.

Novel designation forms are admitted not by ad-hoc write but by OSWG-approved
PR against the referenced latest-OS profile version (DL-013 §1 living-reference
model). Base is SILENT on presence — which designations a subject must bear is
domain territory (per §2 Decision 3).

---

## §3 — Two-relation identifier pattern

**`cp:CarriedIdentifierShape`** — Any node on the far end of `is carrier of`
(BFO_0000101) must be a well-formed designation node. `is carrier of` is a
general BFO relation (a USB stick carries files, a canvas carries paint) —
the base does NOT universally police all carriage, only the co-occurring
two-relation pattern where a document carries an identifier.

**`cp:MatchableIdentifierShape`** — Defines the matchable form. A
person-designated identifier (a node both designated-by a person AND
carried-by a document, or just designated-by) is matchable — it lies on the
identity path DL-012's rulings traverse. A carrier-only node (document carries
it, no person designates it) is a valid *partial write* (conforming-but-non-matchable).
§6 identity conditions bind ONLY to the matchable shape. Domain profiles
attach this shape where a person is on the designated-by path.

---

## §4a — Temporal pattern

**`cp:CalendarDateNodeShape`** — Any node typed as Calendar Date Identifier
(ont00001340) must carry a typed `xsd:date` literal via `has text value`. An
untyped string ("2026-01-01") is non-conforming even if lexically valid — typed
dates are required for date comparison, range validation, and ordering. Existing
untyped date data migrates (the standard demands the semantically honest form).

Known open issue: Paul's California DMV and passport databooks (post-Wave-3
merge, commit ca8da1c) still carry untyped dates — this shape correctly
catches them. The fix (appending `^^xsd:date`) is a confirmed, still-owed
migration item.

---

## §4b — Measurement pattern

**`cp:MeasurementNodeShape`** — A Measurement ICE (ont00001163) must carry
exactly one literal value AND a required measurement-unit reference via
`ont00001812`. The unit is constitutive — a unit-less value is a number, not a
measurement — so requiring it is a shape constraint (base-level), not a
presence constraint deferred to domains.

**Unit relation IRI:** `cco:ont00001863` — "uses measurement unit" from
InformationEntityOntology (domain: `ont00000253` Information Bearing Entity;
range: `ont00000120` Measurement Unit; verified 2026-08-08 against committed
InformationEntityOntology.ttl). This shape is not exercised by any current
Mee instance data, so it has not been end-to-end tested against a real
measurement instance.

---

## §5 — Provenance carriage

**`cp:SCtopicShape`** — Every `topic:SCTopicGraph` must carry exactly one
claimant (the agent making the claim — constitutive, and capped at one because
a claim has a single asserter) and at least one subject (uncapped — a claim may
be about several resources simultaneously).

**Important caveat:** DL-013 §5 requires provenance on object properties, not
annotation properties. Mee's current `topic:claimant` and `topic:subject` are
still `owl:AnnotationProperty` (confirmed at commit ca8da1c). SHACL Core
validates the graph structurally regardless of OWL property-type declarations,
so this shape DOES fire correctly against Mee's synthesized instance data
(pyshacl walks annotation-property triples just like object-property triples).
The migration to object-property carriage is deferred/undecided for
`topic:claimant` and out-of-scope for `topic:subject` (range conflict —
`xsd:anyURI` is a datatype; OWL forbids datatype ranges on ObjectProperty).

---

## §6 — Identity conditions

**`cp:keyingTier`** — A class-level annotation property. Values: `strong`,
`weak`, `non`. Applied to identifier classes (e.g., FAA Unique ID class →
`"strong"`, SSN class → `"weak"`) as the standard's ruling on what a match
on that identifier class licenses (DL-012). This is the standard's ruling, not
a per-instance or per-writer assertion — never assert it on individual nodes.

**`cp:KeyingTierShape`** — Validates that anything annotated with `keyingTier`
carries exactly one valid tier value. Catches mis-typed or missing tier declarations
at the class level.

The profile does NOT detect matches or perform merges — it only validates that
matchable identifier classes correctly declare their tier. All matching and
merging is performed by the implementation, which reads the tier from the class
annotation and applies its own policy (DL-012: "the implementation performs
every merge"). No OWL keys, no reasoner auto-merge, for any tier.

---

## §1 and §7 — Scope and census (documentary, not shapes)

**§1 (Scope/Conformance):** Two conformance classes — record-level (whole
store, base + all applicable per-domain profiles merged) and document-level
(a single credential in isolation, base + its specific profile). Profiles only
TIGHTEN over the base, never relax. The IEEE standard references the latest OS
version; changes are made by OSWG PR vote, not ballot cycle (living-reference
model, DL-013 §1).

**§7 (Census/Deferrals):** Covered domains in this version: identity, contact
(JSContact/RFC 9553 crosswalk substantially pre-done), address. Deferred:
VC use-case profile (after per-domain profiles), resolution policy (Integration
Profile / app layer), deontic type-assertion (cco-d-acts decision pending),
GenderMarker (out of scope, locked). Migrations owed: 5 untyped dates in
Mee's DL/passport databooks.

---

## Known open items before v0.2

1. ~~Verify measurement-unit relation~~ — **resolved 2026-08-08**: correct IRI is `cco:ont00001863` ("uses measurement unit", InformationEntityOntology).
2. The 5 untyped date literals in Mee's DL/passport databooks need `^^xsd:date`
   — a confirmed, still-owed migration (rides into the Wave 3 combined PR or
   separately).
3. `topic:subject` and `topic:claimant` migration to object properties is
   deferred/undecided — the shapes are written for the target state but the
   current Mee data uses annotation properties (which SHACL validates anyway).
4. Per-domain profiles (Person, Address, Staging) not yet built — they tighten
   over this base (add presence requirements, datatype specifics, required
   identifiers) and are the natural next artifacts.
