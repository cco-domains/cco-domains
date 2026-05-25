import os
from rdflib import Graph, URIRef

ONTOLOGY_DIR = "ontology/cco"

# Update these to match your final namespace(s)
EXPECTED_BASES = [
    "https://www.commoncoreontologies.org/",
    "https://w3id.org/cco-domains/",
]

def is_valid_iri(iri: str) -> bool:
    return iri.startswith("http://") or iri.startswith("https://")

def check_iri(iri: str):
    if not is_valid_iri(iri):
        return "Invalid IRI scheme"

    if any(iri.startswith(base) for base in EXPECTED_BASES):
        return None

    return "IRI does not match expected bases"

def main():
    print("🔍 Checking IRI consistency across CCO modules...\n")

    for fname in os.listdir(ONTOLOGY_DIR):
        if not fname.endswith(".ttl"):
            continue

        path = os.path.join(ONTOLOGY_DIR, fname)
        g = Graph()
        g.parse(path, format="turtle")

        print(f"Module: {fname}")

        errors = 0

        for s, p, o in g:
            for term in [s, p, o]:
                if isinstance(term, URIRef):
                    msg = check_iri(str(term))
                    if msg:
                        print(f"  ❌ {msg}: {term}")
                        errors += 1

        if errors == 0:
            print("  ✅ No IRI inconsistencies found.\n")
        else:
            print(f"  ⚠ Found {errors} issues.\n")

if __name__ == "__main__":
    main()
