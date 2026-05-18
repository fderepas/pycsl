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

    args = parser.parse_args()
    if args.command == "build":
        cmd_build(args)
    elif args.command == "query":
        cmd_query(args)
    elif args.command == "chunks":
        cmd_chunks(args)


if __name__ == "__main__":
    main()
