from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from workflows import question_graph, QuestionState

app = FastAPI()

@app.post("/generate_question")
async def generate_question(request: Request):
    try:
        data = await request.json()
        state = QuestionState(
            difficulty=data.get("difficulty", "medium"),
            topic=data.get("topic", "General"),
            skill_tags=data.get("skill_tags", []),
            question_type=data.get("question_type", "multiple_choice"),
            programming_language=data.get("programming_language", "N/A"),
            num_questions=data.get("num_questions", 1),
            output=[]
        )
        result = question_graph.invoke(state)
        return JSONResponse(content={
            "status": "success",
            "question_data": result["output"]
        })
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)