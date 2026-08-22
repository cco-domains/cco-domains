import os
from rdflib import Graph, URIRef

ONTOLOGY_DIR = "ontology/cco"

def get_imports(path):
    g = Graph()
    g.parse(path, format="turtle")

    imports = set()
    for _, _, o in g.triples((None, URIRef("http://www.w3.org/2002/07/owl#imports"), None)):
        imports.add(str(o))
    return imports

def main():
    print("🔍 Checking imports across CCO modules...\n")

    modules = {
        fname: os.path.join(ONTOLOGY_DIR, fname)
        for fname in os.listdir(ONTOLOGY_DIR)
        if fname.endswith(".ttl")
    }

    # Map ontology IRIs to filenames
    ontology_iris = {}
    for fname, path in modules.items():
        g = Graph()
        g.parse(path, format="turtle")
        for ont in g.subjects(predicate=URIRef("http://www.w3.org/2002/07/owl#Ontology")):
            ontology_iris[str(ont)] = fname

    for fname, path in modules.items():
        print(f"Module: {fname}")
        imports = get_imports(path)

        if not imports:
            print("  ⚠ No imports found (check if this is expected).")
            print()
            continue

        for imp in imports:
            if imp not in ontology_iris:
                print(f"  ❌ Import not found in module set: {imp}")
            else:
                print(f"  ✅ Imports module: {ontology_iris[imp]}")

        print()

if __name__ == "__main__":
    main()
