"""
Deals with the engineering puzzles, which need to be imported, served and marked.
"""

import json, glob

answers = {}
with open("puzzles/answers.json", "r") as ans_file:
    answers = json.loads(ans_file.read())

questions = glob.glob("puzzles/*")
questions.remove("puzzles/answers.json")

def attach_answer(question):
    answer = ""
    if question in answers:
        answer = answers[question]
    return (question, answer)

puzzles = list(map(attach_answer, questions))

def load_all_puzzles():
    return puzzles.copy()