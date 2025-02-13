from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
import tempfile
from transformers import pipeline
from assistant import (
    classifier,
    parse_command,
)  # Import classifier and parse_command from assistant
import logging
import time

# print("commands available",classifier.model.config.label2id.keys())

# Configure logging to write INFO-level logs to "info.log"
logging.basicConfig(
    level=logging.INFO,
    filename="info.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)

app = FastAPI()

# Remove or comment out the static mount if there are no static assets:
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the Whisper model once.
transcriber = pipeline("automatic-speech-recognition", "openai/whisper-small.en")


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open("index.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(content=html)


@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    start = time.time()
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        result = transcriber(temp_file.name)
        text = result.get("text", "")
        command = parse_command(text)
    end = time.time()
    logging.info(
        f"Transcribe processed in {end - start:.2f}s, text: '{text}', command: {command}"
    )
    return JSONResponse({"text": text, "command": command})


# New route: /wakeup to detect the wake word using assistant.py's classifier.
@app.post("/wakeup")
async def wakeup(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file.flush()
        # Define wake word parameters:
        wake_word = "marvin"
        threshold = 0.40
        try:
            # Run classifier on the file. Assume classifier returns a list of predictions.
            predictions = classifier(temp_file.name)
            wake_detected = any(
                p["label"].lower() == wake_word and p["score"] > threshold
                for p in (
                    predictions if isinstance(predictions, list) else [predictions]
                )
            )
        except Exception as e:
            wake_detected = False
        return JSONResponse({"wakeup": wake_detected})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="127.0.0.1", port=8080, reload=True)
