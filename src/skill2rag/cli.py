"""
CLI entry point for skill2rag.

Usage:
    skill2rag build
    skill2rag query -q "How to annotate loops?"
    skill2rag chunks
"""

import argparse
import sys


def cmd_build(args):
    from skill2rag.indexer import build_index
    build_index(
        skill_dir=args.skill_dir,
        index_path=args.index,
        model=args.model,
    )


def cmd_query(args):
    from skill2rag.retriever import retrieve_with_scores
    results = retrieve_with_scores(
        query=args.query,
        index_path=args.index,
        top_k=args.top_k,
        model=args.model,
    )
    for i, (chunk, score) in enumerate(results, 1):
        path = chunk.display_path()
        print(f"\n{'='*60}")
        print(f"[{i}] {path}  (score: {score:.4f}, {len(chunk.content)} chars)")
        print(f"{'='*60}")
        if args.full:
            print(chunk.content)
        else:
            preview = chunk.content[:300]
            if len(chunk.content) > 300:
                preview += "..."
            print(preview)


def cmd_chunks(args):
    from skill2rag.chunker import chunk_directory
    chunks = chunk_directory(args.skill_dir)
    print(f"Total chunks: {len(chunks)}\n")
    for c in chunks:
        print(f"  [{c.source_file}] L{c.level} {c.title} ({len(c.content)} chars)")


def cmd_verify(args):
    """Check the index is complete + fresh vs the live skill tree.

    Exit codes: 0 in sync · 1 drift (missing skills / unindexed / stale) ·
    2 index file absent.
    """
    from skill2rag.verify import verify_index
    ok, r = verify_index(skill_dir=args.skill_dir, index_path=args.index)

    if r.get("index_missing"):
        print(f"[!] RAG index not found at {r['index_path']} — run `make rag-build` first.")
        sys.exit(2)

    print(f"=== RAG index verify ({r['index_path']}) ===")
    print(f"skills: {r['skills_total']}  |  current chunks: {r['current_chunks']}  "
          f"|  indexed chunks: {r['index_chunks']}")

    def _section(label, items, limit=15):
        print(f"  {label}: {len(items)}")
        for x in items[:limit]:
            print(f"      - {x}")
        if len(items) > limit:
            print(f"      … and {len(items) - limit} more")

    _section("missing skills (no chunk in index)", r["missing_skills"])
    _section("unindexed (new content, never built)", r["unindexed"])
    _section("stale (source edited since build)", r["stale"])
    _section("orphan (in index, gone from tree) [warn]", r["orphan"])

    if ok:
        warn = " (orphans present — rebuild to prune)" if r["orphan"] else ""
        print(f"[+] RAG index is complete and fresh{warn}.")
        sys.exit(0)
    print("[!] RAG index is stale — run `make rag-build`.")
    sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="skill2rag",
        description="Hybrid RAG for LLM skills",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # build
    p_build = sub.add_parser("build", help="Build the vector index from skill files")
    p_build.add_argument("--skill-dir", default="./config/skills", help="Directory with .md skill files")
    p_build.add_argument("--index", default="./data/embeddings/skills_index.json", help="Output index JSON path")
    p_build.add_argument("--model", default="nomic-embed-text", help="Embedding model")

    # query
    p_query = sub.add_parser("query", help="Query the index for relevant skill chunks")
    p_query.add_argument("--index", default="./data/embeddings/skills_index.json", help="Index JSON path")
    p_query.add_argument("-q", "--query", required=True, help="Search query")
    p_query.add_argument("--top-k", type=int, default=5, help="Number of results")
    p_query.add_argument("--model", default=None, help="Embedding model override")
    p_query.add_argument("--full", action="store_true", help="Show full chunk content")

    # chunks
    p_chunks = sub.add_parser("chunks", help="List chunks without building an index")
    p_chunks.add_argument("--skill-dir", default="./config/skills", help="Directory with .md skill files")

    # verify
    p_verify = sub.add_parser("verify", help="Check the index is complete + fresh (no embedding)")
    p_verify.add_argument("--skill-dir", default="./config/skills", help="Directory with .md skill files")
    p_verify.add_argument("--index", default="./data/embeddings/skills_index.json", help="Index JSON path")

    args = parser.parse_args()
    if args.command == "build":
        cmd_build(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "chunks":
        cmd_chunks(args)
    elif args.command == "verify":
        cmd_verify(args)


if __name__ == "__main__":
    main()
