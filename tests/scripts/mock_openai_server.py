from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
from docmancer.generators.llm.prompt import Prompt

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: List[Message]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 1000

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str = "stop"

class Usage(BaseModel):
    prompt_tokens: int = 100
    completion_tokens: int = 50
    total_tokens: int = 150

class ChatResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[Choice]
    usage: Usage

def get_expected_json_response():
    prompt = Prompt()
    return prompt._get_expected_json_format()

@app.post("/v1/chat/completions")
async def chat_completion(
    request: ChatRequest,
    authorization: str = Header(None)
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Mock response for documentation generation
    response = ChatResponse(
        id=f"mock-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        created=int(datetime.now().timestamp()),
        model=request.model,
        choices=[
            Choice(
                index=0,
                message=Message(
                    role="assistant",
                    content=get_expected_json_response()
                )
            )
        ],
        usage=Usage()
    )
    
    return response

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)