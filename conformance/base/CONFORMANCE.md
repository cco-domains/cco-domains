# CCO-Domains Conformance

## What this is

Shared vocabulary is necessary for data interoperability but not sufficient.
Two systems can use the same CCO-Domains term and still produce data the other
cannot read, because the ontology defines what a term *means* and says nothing
about how instance data must be *shaped*. The Base Conformance Profile closes
that gap.

It is a SHACL artifact that specifies the structural requirements instance data
must satisfy to be interoperable across any CCO-conformant domain — persons,
addresses, airmen, facilities, artifacts, events, or any other domain whose
terms are built over CCO patterns.

The profile constrains those patterns directly:

- How a designation attaches to what it designates
- How an identifier borne by a document relates to the entity it individuates
- How a date or a measurement must be expressed
- How a claim carries its subject and claimant
- What a match on a given identifier class is permitted to license

None of these are domain-specific constraints. They are the shared CCO
structural patterns — the same patterns that appear in every domain ontology
built over CCO — and they apply wherever those patterns appear, regardless
of domain. An application that writes conforming data can be read by an
application that never coordinated with its author.

**Files:**
- `CCO-Domains_Base_Conformance_Profile_v0_1.ttl` — the normative shapes
- `CCO-Domains_Base_Conformance_Profile_Rationale.md` — reasoning, caveats, open items

---

## Where this is headed

The profile is intended to become a normative companion standard to the
CCO-Domains domain ontologies, via one of two paths:

**IEEE** — a companion standard under its own PAR, separate from the ontology
PARs. This is the conventional structure: the thing being profiled and the
conformance rules that govern its use are separate documents with separate
governance, because they evolve at different rates. Data interoperability is
explicitly what a PAR of this kind exists to establish.

**W3C Community Group** — a Community Specification published under CC-BY 4.0
with an open review process. This is a viable terminal state, not merely a
fallback. A conformance profile with real implementations and a working
validation story is a de facto standard whether or not a standards body has
balloted it.

Which path is taken depends on adoption and on how the standardization
environment develops. Both remain open. The profile is being built to be
correct on its own terms in either case.

---

## Status

v0.1. Built 2026-08-08 against the `w3id.org/cco-domains` namespace,
rdflib-parse-validated, and tested end-to-end with pyshacl against real
instance data from an independent implementation.

### Profile family

The base profile is the foundation of a composable family:

```
Base Conformance Profile (this document — universal, domain-agnostic)
    ↑ tightened by
Per-Domain Profiles (Person, Address, Airman, Facility... — in development)
    ↑ tightened by
Use-Case Profiles (VC issuance, KG publication, regulatory... — future)
```

Per-domain profiles add presence requirements, datatype specifics, and
required identifiers for their domain. They tighten over the base and
never relax it. The base's guarantees apply across all of them.

---

## Running it

Any SHACL 1.0-compliant processor. The profile requires no OWL reasoning and
is not designed for an OWL editor — Protégé will show almost nothing, because
SHACL shapes are not OWL constructs. Use a SHACL tool.

```bash
pyshacl -s CCO-Domains_Base_Conformance_Profile_v0_1.ttl your-data.ttl
```

Conformance test results against known implementations are published separately
as dated artifacts in `conformance/results/`.

---

## Note on independent implementations

Where the profile and an independent implementation disagree, that disagreement
is information the profile should take seriously. Several of the base profile's
constraints were sharpened by contact with existing implementations, and the
current open items in the rationale document reflect unresolved questions that
real data surfaces. The profile is not the last word on any of these questions;
it is the current best answer, subject to revision as evidence accumulates.

---

*CCO-Domains is developed by Global Research, Inc., a 501(c)(3) nonprofit.
Licensed CC-BY 4.0. https://w3id.org/cco-domains*
