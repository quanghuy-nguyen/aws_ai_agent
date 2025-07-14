import os
import shutil
import uvicorn
from mangum import Mangum
from pathlib import Path
from pydantic import BaseModel 
from typing import List
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from ai_agent import get_agent_executor, initial_message
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi import HTTPException

memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
memory.chat_memory.add_message(SystemMessage(content=initial_message))

agent_executor = get_agent_executor(memory=memory)

app = FastAPI()
handler = Mangum(app)

IS_USING_IMAGE_RUNTIME = None
IS_USING_IMAGE_RUNTIME = os.getenv('IS_USING_IMAGE_RUNTIME', None)

if IS_USING_IMAGE_RUNTIME is not None:
    IMAGE_PATH = '/tmp/images/'
    REPORT_PATH = '/tmp/reports/'
else:
    IMAGE_PATH = 'images/'
    REPORT_PATH = 'reports/'

UPLOAD_FOLDER = Path(IMAGE_PATH)
UPLOAD_FOLDER.mkdir(exist_ok=True)

REPORT_FOLDER = Path(REPORT_PATH)
REPORT_FOLDER.mkdir(exist_ok=True)


@app.get("/")
def index():
    return {"message": "Welcome! Use /analyze_images or /chat to interact with AI agent."}

@app.post("/upload_images")
async def upload_images(files: List[UploadFile] = File(...)):
    saved_paths = []
    try:
        for file in files:
            path = UPLOAD_FOLDER / file.filename
            with open(path, "wb") as f:
                shutil.copyfileobj(file.file, f)
            saved_paths.append(file.filename)

        return {"message": f"{len(saved_paths)} files uploaded successfully.", "files": saved_paths}
    except Exception as e:
        return {"error": str(e)}

class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
async def chat_with_agent(request: ChatRequest):
    global memory

    try:
        user_input = request.message
        result = agent_executor.invoke({"input": user_input})
        response = result["output"]
        memory.chat_memory.add_message(HumanMessage(content=user_input))
        memory.chat_memory.add_message(AIMessage(content=response))

        return {"response": response}

    except Exception as e:
        return {"error": str(e)}

@app.get("/download_report", response_class=FileResponse)
def download_latest_report():
    report_files = sorted(REPORT_FOLDER.glob("*.txt"), key=os.path.getmtime, reverse=True)
    if not report_files:
        raise HTTPException(status_code=404, detail="No reports found.")

    latest_report = report_files[0]

    return FileResponse(
        path=latest_report,
        filename=latest_report.name,
        media_type="text/plain"
    )


# === Chạy local ===
if __name__ == "__main__":
    port = 8000
    print(f"Running FastAPI server on http://localhost:{port}")
    uvicorn.run("app_api_handler:app", host="0.0.0.0", port=port, reload=True)
