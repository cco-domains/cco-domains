#!/usr/bin/env python3
"""
generate_term_snippets.py — CCO-Domains per-term IRI resolution

Generates one small TTL + JSON-LD document per minted term, so that a single
entity IRI (e.g. https://w3id.org/cco-domains/cco/ent00000001) dereferences to
just that term rather than to its whole containing module.

Canonical source is always the authored Turtle in ontology/. These snippets are
GENERATED ARTIFACTS — never hand-edit them; edit the ontology and re-run.

Each snippet is the Concise Bounded Description (CBD) of the term: every triple
with the term as subject, plus the transitive closure of any blank nodes
reached (OWL restrictions, unions, intersections, RDF lists), so axioms survive
intact instead of dangling.

Usage:
    python generate_term_snippets.py [--repo-root PATH] [--check]

    --check   Generate into a temp dir and diff against what is committed.
              Exits non-zero if they differ. Used by CI to prove the committed
              snippets match the ontologies.
"""

import argparse
import json
import shutil
import sys
import tempfile
from pathlib import Path

from rdflib import Graph, URIRef, BNode, Namespace
from rdflib.namespace import OWL, RDF, RDFS, SKOS, DCTERMS, XSD

# Terms live under this namespace regardless of which file defines them.
TERM_NS = "https://w3id.org/cco-domains/cco/"

# Directories holding authored ontology content, relative to repo root.
SOURCE_DIRS = ["ontology/cco", "ontology/domains"]

# Where snippets are written, relative to repo root.
OUTPUT_DIR = "ontology/terms"

# Prefixes bound on every snippet so the output stays readable.
PREFIXES = {
    "cco": TERM_NS,
    "owl": str(OWL),
    "rdf": str(RDF),
    "rdfs": str(RDFS),
    "skos": str(SKOS),
    "dcterms": str(DCTERMS),
    "xsd": str(XSD),
    "obo": "http://purl.obolibrary.org/obo/",
    "dc": "http://purl.org/dc/elements/1.1/",
}

JSONLD_CONTEXT = {
    "cco": TERM_NS,
    "owl": str(OWL),
    "rdfs": str(RDFS),
    "skos": str(SKOS),
    "dcterms": str(DCTERMS),
    "obo": "http://purl.obolibrary.org/obo/",
}


def load_source_graph(repo_root: Path) -> Graph:
    """Parse every authored .ttl under SOURCE_DIRS into one graph."""
    g = Graph()
    files = []
    for rel in SOURCE_DIRS:
        d = repo_root / rel
        if not d.is_dir():
            continue
        files.extend(sorted(d.glob("*.ttl")))

    if not files:
        sys.exit(f"ERROR: no .ttl files found under {SOURCE_DIRS} in {repo_root}")

    for f in files:
        try:
            g.parse(f, format="turtle")
        except Exception as e:
            sys.exit(f"ERROR: failed to parse {f}: {e}")

    print(f"Parsed {len(files)} ontology files -> {len(g)} triples")
    return g


def find_terms(g: Graph) -> list:
    """
    Every subject in the term namespace that this repo actually defines.

    A term counts as defined if it carries an rdf:type — that filters out IRIs
    which merely appear as objects of a reference (e.g. an imported parent that
    lives upstream) and would otherwise yield an empty, misleading snippet.
    """
    terms = set()
    for s in g.subjects(RDF.type, None):
        if isinstance(s, URIRef) and str(s).startswith(TERM_NS):
            local = str(s)[len(TERM_NS):]
            # Skip module-level identifiers and any nested path; terms are flat ids.
            if "/" in local or "#" in local or not local:
                continue
            terms.add(s)
    return sorted(terms, key=str)


def concise_bounded_description(g: Graph, term: URIRef) -> Graph:
    """
    CBD of `term`: its own triples plus the full blank-node closure beneath them.

    Without the closure an OWL restriction serialises as a reference to a blank
    node whose contents live in another file, so the axiom is silently lost.
    """
    out = Graph()
    for prefix, ns in PREFIXES.items():
        out.bind(prefix, Namespace(ns))

    pending = [term]
    seen_bnodes = set()

    while pending:
        node = pending.pop()
        for p, o in g.predicate_objects(node):
            out.add((node, p, o))
            if isinstance(o, BNode) and o not in seen_bnodes:
                seen_bnodes.add(o)
                pending.append(o)

    return out


def _bnode_signature(g: Graph, node, depth: int = 0) -> str:
    """
    Content-derived signature for a blank node, used to name it deterministically.

    rdflib mints a random label for every blank node on every run, so identical
    input would otherwise serialise to different bytes each time and --check
    would report drift that isn't real. Recursion is depth-capped because OWL
    list structures can be deep and, in malformed data, cyclic.
    """
    if depth > 12:
        return "..."
    parts = []
    for p, o in sorted(g.predicate_objects(node), key=lambda x: (str(x[0]), str(x[1]))):
        if isinstance(o, BNode):
            parts.append(f"{p}->({_bnode_signature(g, o, depth + 1)})")
        else:
            parts.append(f"{p}->{o}")
    return "|".join(parts)


def relabel_bnodes(g: Graph) -> Graph:
    """Replace random blank-node labels with stable b0, b1, ... by signature."""
    bnodes = {n for t in g for n in t if isinstance(n, BNode)}
    if not bnodes:
        return g

    ordered = sorted(bnodes, key=lambda n: (_bnode_signature(g, n), str(n)))
    mapping = {n: BNode(f"b{i}") for i, n in enumerate(ordered)}

    out = Graph()
    for prefix, ns in g.namespaces():
        out.bind(prefix, ns)
    for s, p, o in g:
        out.add((mapping.get(s, s), p, mapping.get(o, o)))
    return out


def _canonicalise(node):
    """
    Recursively sort a parsed JSON-LD structure so output is byte-stable.

    Lists are sorted by their serialised form, which gives a total order over
    mixed content (strings, dicts, nested lists) without needing them to be
    mutually comparable. Dict key order is handled by json.dumps(sort_keys=True).
    """
    if isinstance(node, dict):
        out = {}
        for k, v in node.items():
            # @list encodes an rdf:first/rdf:rest chain, where order is part of
            # the data — OWL intersections and unions are serialised this way.
            # Sorting it would silently rewrite the axiom, so recurse into the
            # members but leave their sequence alone.
            if k == "@list" and isinstance(v, list):
                out[k] = [_canonicalise(item) for item in v]
            else:
                out[k] = _canonicalise(v)
        return out
    if isinstance(node, list):
        items = [_canonicalise(v) for v in node]
        return sorted(items, key=lambda x: json.dumps(x, sort_keys=True, ensure_ascii=False))
    return node


def write_snippets(g: Graph, terms: list, out_dir: Path) -> int:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = 0

    for term in terms:
        local = str(term)[len(TERM_NS):]
        cbd = concise_bounded_description(g, term)

        if len(cbd) == 0:
            print(f"  WARN: {local} produced an empty description; skipped")
            continue

        cbd = relabel_bnodes(cbd)

        # Turtle
        (out_dir / f"{local}.ttl").write_bytes(
            cbd.serialize(format="turtle", encoding="utf-8")
        )

        # JSON-LD. Pass the context to rdflib so keys compact to cco:/rdfs:/etc
        # rather than expanding to full IRIs, and use auto_compact so the output
        # is a single node object where possible instead of a bare array.
        #
        # rdflib does not guarantee a stable ordering, so sort recursively before
        # writing — otherwise byte-identical inputs produce different files on
        # each run and --check reports spurious drift.
        raw = json.loads(
            cbd.serialize(format="json-ld", context=JSONLD_CONTEXT, auto_compact=True)
        )
        (out_dir / f"{local}.jsonld").write_text(
            json.dumps(_canonicalise(raw), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        written += 1

    return written


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo-root", default=".", type=Path)
    ap.add_argument("--check", action="store_true",
                    help="verify committed snippets match the ontologies")
    args = ap.parse_args()

    repo_root = args.repo_root.resolve()
    g = load_source_graph(repo_root)
    terms = find_terms(g)
    print(f"Found {len(terms)} defined terms in {TERM_NS}")

    committed = repo_root / OUTPUT_DIR

    if args.check:
        tmp = Path(tempfile.mkdtemp())
        n = write_snippets(g, terms, tmp)
        print(f"Generated {n} snippets into a temporary directory for comparison")

        if not committed.is_dir():
            shutil.rmtree(tmp)
            sys.exit(f"FAIL: {OUTPUT_DIR} does not exist. Run without --check and commit.")

        gen = {p.name for p in tmp.iterdir()}
        com = {p.name for p in committed.iterdir() if p.suffix in (".ttl", ".jsonld")}

        problems = []
        for name in sorted(gen - com):
            problems.append(f"  missing from repo: {name}")
        for name in sorted(com - gen):
            problems.append(f"  stale in repo (no longer generated): {name}")
        for name in sorted(gen & com):
            if (tmp / name).read_bytes() != (committed / name).read_bytes():
                problems.append(f"  out of date: {name}")

        shutil.rmtree(tmp)

        if problems:
            print("\nFAIL: committed snippets do not match the ontologies:")
            print("\n".join(problems[:50]))
            if len(problems) > 50:
                print(f"  ... and {len(problems) - 50} more")
            print("\nRun: python ontology/tools/generate_term_snippets.py")
            sys.exit(1)

        print("OK: committed snippets match the ontologies")
        return

    # Regenerate from scratch so deleted terms don't leave orphans behind.
    if committed.is_dir():
        shutil.rmtree(committed)

    n = write_snippets(g, terms, committed)
    print(f"Wrote {n} terms ({n * 2} files) to {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
