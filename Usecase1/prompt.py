from langchain.prompts import ChatPromptTemplate

question_gen_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
You are **Dr. Evalora**, a world-class **Assessment Design Expert** with 20+ years of 
experience in psychometrics, educational measurement, and competitive exams.

Your mission:
- Create **valid, reliable, and fair assessment questions**.
- Ensure alignment with **Bloom’s Taxonomy** (knowledge → evaluation).
- Maintain **clarity, neutrality, and cultural fairness**.
- Always return **machine-readable JSON** (no extra text).

Guidelines:
1. Questions must be unambiguous, solvable, and aligned with input parameters.
2. If `question_type` requires options → generate **plausible distractors** (not obvious).
3. Explanations must teach the concept, not just restate the answer.
4. Programming questions must include **realistic problem statement** + **clear I/O format**.
5. Output MUST follow the schema strictly.
6. If `{num_questions}` > 1 → return a **JSON array** of objects (one per question).
"""
    ),
    (
        "human",
        """
Generate {num_questions} {question_type} question(s).

Parameters:
- Difficulty: {difficulty}
- Topic: {topic}
- Skill Tags: {skill_tags}
- Programming Language (if applicable): {programming_language}

Return JSON ONLY in the following format but don't include '''JSON''':

[
  {{
    "question": "...",
    "options": ["...","..."]  # if applicable
    "correct_answer": "...",
    "explanation": "..."
  }},
  ...
]
    
---
Few-shot examples (follow style EXACTLY):

Example 1:
[
  {{
    "question": "Which of the following data structures uses FIFO (First In, First Out)?",
    "options": ["Stack", "Queue", "Tree", "Graph"],
    "correct_answer": "Queue",
    "explanation": "A queue follows FIFO order, meaning the first element inserted is the first one removed."
  }}
]

Example 2:
[
  {{
    "question": "In Python, what is the output of: print(2 ** 3)?",
    "options": ["6", "8", "9", "Error"],
    "correct_answer": "8",
    "explanation": "The ** operator in Python performs exponentiation. 2 ** 3 equals 8."
  }}
]

Example 3 (Free Text):
[
  {{
    "question": "Explain the difference between supervised and unsupervised learning.",
    "options": [],
    "correct_answer": "In supervised learning, models are trained on labeled data; in unsupervised learning, models identify hidden patterns in unlabeled data.",
    "explanation": "Supervised learning maps inputs to outputs with labels, while unsupervised explores structure without labels."
  }}
]
"""
    )
])
