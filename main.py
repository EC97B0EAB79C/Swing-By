#!/usr/bin/env python3

from src.cli.parser import parse_args

from src.utils.config import Config

from src.knowledge.base import KnowledgeBase
from src.knowledge.factory import KnowledgeFactory

def main():
    args = parse_args()

    kb = KnowledgeBase(
        KnowledgeFactory.create(
            Config.type()
        )
    )
    kb.process_updated_files()

    while True:
        query = input("Q: ")
        if query == "":
            continue
        if query == "exit":
            break
        result = kb.qna(query)
        print("SB:\n", result["answer"])
        for idx, ref in enumerate(result.get("references", [])):
            print(f"- [{idx+1}] {ref}")

if __name__ == "__main__":
    main()
