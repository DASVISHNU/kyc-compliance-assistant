# Ask the RBI KYC assistant from the terminal.
#   One question:   uv run python scripts\ask.py "How often should KYC be updated for high-risk customers?"
#   Chat mode:      uv run python scripts\ask.py
import sys

from rag.retrieve.retriever import load_index
from rag.generate.answer import answer_question


def print_result(result):
    print("\nAnswer:\n" + result["answer"])
    print("\nSources:")
    for source in result["sources"]:
        pages = source["pages"]
        if len(pages) == 1:
            page_text = "page " + str(pages[0])
        else:
            page_text = "pages " + str(pages[0]) + "-" + str(pages[-1])
        print("  [" + str(source["number"]) + "] " + source["label"] + ", " + page_text)


index = load_index()                     # load once, reuse for every question

if len(sys.argv) >= 2:
    print_result(answer_question(sys.argv[1], index))
else:
    print("RBI KYC Assistant. Type a question, or 'exit' to quit.")
    print("For information only. Not legal or compliance advice.")
    while True:
        question = input("\nYou: ").strip()
        if question.lower() in ["exit", "quit"]:
            break
        if question == "":
            continue
        print_result(answer_question(question, index))