# CCO-Domains Ontology QA Scripts

This folder contains quality‑assurance scripts used to validate the
ontology modules in `ontology/cco/` before running the per‑entity
extraction pipeline.

These scripts help ensure that:

1. All IRIs use the correct base namespace.
2. No outdated or malformed IRIs remain.
3. All OWL imports across the 11 CCO modules are correct.
4. No modules import nonexistent or incorrect ontology IRIs.

## Scripts

### 1. check_iri_consistency.py
Validates that all IRIs in the ontology modules:

- Use the correct base namespace(s)
- Do not contain old or deprecated IRIs
- Are syntactically valid
- Do not contain illegal characters

Run with:


### 2. check_imports.py
Validates that:

- All imports reference actual ontology modules
- No module imports itself
- No module imports a nonexistent ontology
- No circular imports exist

Run with:


## Expected Directory Layout

