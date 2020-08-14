"""
Deals with the engineering puzzles, which need to be imported, served and marked.
"""

import json, glob
from random import choice

answers = {}
with open("puzzles/answers.json", "r") as ans_file:
    answers = json.loads(ans_file.read())

questions = glob.glob("puzzles/*")
questions.remove("puzzles/answers.json")

def attach_answer(question):
    answer = []
    if question in answers:
        answer = answers[question]
        if type(answer) is str:
            answer = [answer]
        for i in range(len(answer)):
            answer[i] = answer[i].lower()
    return (question, answer)

puzzles = list(map(attach_answer, questions))

def load_all_puzzles():
    return puzzles.copy()

class EngineeringPuzzles():
    def __init__(self, sub):
        self.sub = sub
        self.puzzles = load_all_puzzles()
        self.current_puzzle = None
        self.puzzle_reason = ""
        # wear_and_tear is a counter until we introduce a puzzle!
        self.wear_and_tear = 5

    async def movement_tick(self):
        # When we move, we need to reset puzzles and set new ones.
        # Puzzles resolve once you've moved:
        await self.resolve_puzzle(None)
        # We also need to set wear and tear puzzles if need be.
        self.wear_and_tear -= 1
        if self.wear_and_tear <= 0:
            await self.send_puzzle("wear and tear")
            self.wear_and_tear = choice([4,5,6])
    
    async def send_puzzle(self, reason):
        """
        Send the next puzzle, tagging it with a reason.
        Valid reasons are:
        * "wear and tear" - done every few moves. Penalty is a damage if ignored or failed, nothing if correct.
        * "repair" - whenever the engineer asks for it. Penalty is a damage if failed, nothing if ignored, and one healing if correct.
        * "fixing" - whenever control asks for it. Penalty is the same as wear and tear.
        If there is a puzzle in progress, that puzzle immediately resolves (as if you ran out of time).
        """
        if self.current_puzzle:
            await self.resolve_puzzle(None)
        if len(self.puzzles) == 0:
            self.puzzles = load_all_puzzles()
        
        puzzle_to_deliver = self.puzzles[0]
        self.puzzles = self.puzzles[1:]
        self.current_puzzle = puzzle_to_deliver
        self.puzzle_reason = reason
        await self.sub.send_message(f"Puzzle for **{reason}** received! You have until your submarine next moves to solve it!", "engineer", self.current_puzzle[0])
        return True
    
    async def resolve_puzzle(self, answer):
        """
        Resolve the current puzzle, if able. Called with answer=None if time ran out.
        """
        if self.current_puzzle is None:
            return False
        
        condition = self.puzzle_reason.capitalize()
        if answer is not None and answer.lower() in self.current_puzzle[1]:
            # Correct!
            if condition == "Repair":
                await self.sub.send_to_all(self.sub.power.heal(1))
            await self.sub.send_message(f"Puzzle answered correctly! **{condition}** sorted!", "engineer")
        else:
            # Incorrect.
            if answer is None:
                await self.sub.send_message(f"Ran out of time to solve puzzle. **{condition}** not sorted.", "engineer")
                if condition != "Repair":
                    await self.sub.send_to_all(self.sub.power.damage(1))
            else:
                await self.sub.send_message(f"You got the answer wrong! **{condition}** not sorted.", "engineer")
                await self.sub.send_to_all(self.sub.power.damage(1))
            self.puzzles.append(self.current_puzzle)
        self.current_puzzle = None
        return True
    