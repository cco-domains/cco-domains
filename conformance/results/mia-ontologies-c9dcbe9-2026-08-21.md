# Conformance Test Result — MeeFoundation/mia-ontologies

**Profile family:** CCO-Domains Conformance Profile v0.1
**Profile files authored:** 2026-08-21 (Jim Schoening, Global Research Inc.)
**Implementation:** MeeFoundation/mia-ontologies
**Commit:** c9dcbe9 (2026-08-21)
**Test date:** 2026-08-21
**Tool:** pyshacl, SHACL Core, inference=none
**Scope:** 19 substantive cell-databooks under `example/Cells/**/*.databook.md`
  (17 additional placeholder databooks contain no Turtle content — correctly excluded)

**Note on prior test result:** An earlier validation run was performed against
commit `eae43d5` (2026-08-08) using the base profile only. This file supersedes
that result with full four-profile coverage against the current commit.

---

## Summary by profile

| Profile | Shapes | Conforming | Non-conforming |
|---|---|---|---|
| Base Conformance Profile | 8 | 13 | 6 |
| Person Domain Profile | 4 | 17 | 2 |
| Address Domain Profile | 6 | 19 | 0 |
| Staging Domain Profile | 11 | 18 | 1 |

Results are identical to the prior run against commit `eae43d5` — Paul's
2026-08-21 changes (removal of `p:hasPaymentCard`, `p:CheckingAccountNumber`,
`p:RoutingNumber` from persona.ttl; deletion of group.ttl) did not affect
any validation outcomes. No Group instances appear in databook Turtle content;
the removed Staging-profile target classes simply have no instances to fire on.

---

## Base Conformance Profile — 13 of 19 conforming

### Fully conforming (13)
ATT, Alice Walker (employee), Bob Johnson, Fred Flintstone, Google,
Health & Wellness, Jane Starostina, Medical Appointment, Ownership,
Paula Walker (employee), Paula Walker (family), SSA, Texas Vital Records

### Non-conforming (6)

**Date typing — 3 databooks:**

| Databook | Value | Fix |
|---|---|---|
| California DMV (drivers-license) line 90 | `"2031-07-04"` | Add `^^xsd:date` |
| Department of State (passport) line 90 | `"2021-07-04"` | Add `^^xsd:date` |
| Department of State (passport) line 95 | `"2031-07-04"` | Add `^^xsd:date` |
| Citibank (banking-payments) | `"12/28"` | Domain decision needed — not ISO 8601 |

**Address designation structure — 3 databooks:**
Boston, Paradise, and BHS address databooks use a composite address model.
This is an open architectural question — not a simple defect. The Address
domain profile resolves this by adopting the component model (Option A),
under which all three databooks fully conform. No fix proposed pending
resolution of the Address Designation architectural question.

---

## Person Domain Profile — 17 of 19 conforming

### Non-conforming (2)

**Birthdate typing — 2 databooks:**
Birthdate nodes (`cco:ent00000046`) carry untyped date strings. The base
profile misses these because they are typed as `ent00000046` (Birthdate)
rather than `ont00001340` (Calendar Date Identifier). The Person domain
profile catches them directly via `cp:BirthdateNodeShape`.

| Databook | Value | Fix |
|---|---|---|
| California DMV (drivers-license) line 85 | `"1985-07-04"` | Add `^^xsd:date` |
| Department of State (passport) line 85 | `"1985-07-04"` | Add `^^xsd:date` |

---

## Address Domain Profile — 19 of 19 conforming

All address component nodes carry exactly one literal value when present.
`cp:AddressDesignationShape` dropped (Option A) — composite address model
is architecturally valid; single canonical string not required at base level.

---

## Staging Domain Profile — 18 of 19 conforming

### Non-conforming (1)

**Service URI stored as string literal — 1 databook:**

| Databook | Value | Fix |
|---|---|---|
| Citibank (banking-payments) | `"https://online.citi.com"` | Change to `<https://online.citi.com>` |

**Note on removed terms:** Paul removed `p:CheckingAccountNumber` and
`p:RoutingNumber` from persona.ttl on 2026-08-21. The Staging profile shapes
`cp:CheckingAccountNumberShape` and `cp:RoutingNumberShape` now target classes
no longer present in his implementation — they are harmless orphans (SHACL
finds no instances to fire on) consistent with Staging's transit-zone nature.
These shapes will be retired when the terms are formally removed from
StagingOntology or find permanent homes elsewhere.

---

## Consolidated fix list for PR to Paul

| Databook | Fix |
|---|---|
| California DMV line 85 | `"1985-07-04"` → `"1985-07-04"^^xsd:date` |
| California DMV line 90 | `"2031-07-04"` → `"2031-07-04"^^xsd:date` |
| Department of State line 85 | `"1985-07-04"` → `"1985-07-04"^^xsd:date` |
| Department of State line 90 | `"2021-07-04"` → `"2021-07-04"^^xsd:date` |
| Department of State line 95 | `"2031-07-04"` → `"2031-07-04"^^xsd:date` |
| Citibank service URI | `"https://online.citi.com"` → `<https://online.citi.com>` |
| Citibank expiration date | `"12/28"` → domain decision needed |

---

## Observations

1. **68% of databooks fully conform to the base profile** without any changes.
2. **100% conform to the Address domain profile** under the component model.
3. **The Person domain profile caught violations the base profile missed** —
   demonstrating the value of domain profiles composing over the base.
4. **The Staging domain profile identified a URI-vs-literal distinction** not
   caught by any other profile.
5. **Paul's 2026-08-21 changes had no adverse effect** on any conformance result.
6. **All violations are in example/worked data**, not in the ontology files.
