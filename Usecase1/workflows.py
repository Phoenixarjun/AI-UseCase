from typing import TypedDict
from langgraph.graph import StateGraph, END
from llm import llm
from prompt import question_gen_prompt
import json
import re

class QuestionState(TypedDict):
    difficulty: str
    topic: str
    skill_tags: list[str]
    question_type: str
    programming_language: str
    num_questions: int  
    output: list[dict]  

def clean_gemini_response(response_content: str):
    if not response_content:
        return []
    
    cleaned = re.sub(r'```json|```', '', response_content).strip()
    
    json_match = re.search(r'(\[.*\]|\{.*\})', cleaned, re.DOTALL)
    if json_match:
        cleaned = json_match.group(1)
    
    try:
        parsed = json.loads(cleaned)
        return parsed if isinstance(parsed, list) else [parsed]
    except json.JSONDecodeError:
        return [{"question": response_content}]

def generate_question(state: QuestionState) -> dict:
    prompt = question_gen_prompt.format(
        difficulty=state["difficulty"],
        topic=state["topic"],
        skill_tags=", ".join(state["skill_tags"]),
        question_type=state["question_type"],
        programming_language=state.get("programming_language", "N/A"),
        num_questions=state.get("num_questions", 1)
    )

    response = llm.invoke(prompt)
    
    parsed = clean_gemini_response(response.content)
    
    formatted_questions = []
    for q in parsed:
        if not isinstance(q, dict):
            q = {"question": str(q)}
        
        formatted_q = {
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "correct_answer": q.get("correct_answer", ""),
            "explanation": q.get("explanation", "")
        }
        formatted_questions.append(formatted_q)
    
    return {"output": formatted_questions}

workflow = StateGraph(QuestionState)
workflow.add_node("generate_question", generate_question)
workflow.set_entry_point("generate_question")
workflow.add_edge("generate_question", END)

question_graph = workflow.compile()