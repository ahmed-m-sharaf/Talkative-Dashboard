from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from engine import dashboard_engine
from schemas import DashboardResponse

app = FastAPI(
    title="Talkative Chatbot API",
    description="REST API for the Talkative Recruitment Analytics Dashboard Engine",
    version="1.0.0"
)

class ChatRequest(BaseModel):
    prompt: str

@app.post("/api/chat", response_model=DashboardResponse)
def chat(request: ChatRequest):
    if not request.prompt or not request.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")
    try:
        response = dashboard_engine.run(request.prompt)
        return response
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health():
    return {"status": "healthy"}
