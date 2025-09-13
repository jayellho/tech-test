from typing import Union
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import os
import tempfile
import librosa
import numpy as np
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
from datasets import load_dataset
import torch
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()
STT_MODEL = os.getenv("STT_MODEL")
print(f"Using STT model: {STT_MODEL}")
SAMPLE_RATE = int(os.getenv("SAMPLE_RATE", "16000"))
SUPPORTED_FILE_FORMATS = (".mp3", ".wav", ".flac", ".ogg", ".webm", ".opus")

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

def transcribe(audio_16k):
    print("Loading model...")
    processor = Wav2Vec2Processor.from_pretrained(STT_MODEL)
    model = Wav2Vec2ForCTC.from_pretrained(STT_MODEL)
    input_values = processor(audio_16k, sampling_rate=SAMPLE_RATE, return_tensors="pt", padding=True).input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    print("Decoding...")
    transcription = processor.batch_decode(predicted_ids)[0]
    return transcription.strip()


def resample_audio(audio_path, sample_rate):
    audio, _ = librosa.load(audio_path, sr=sample_rate, mono=True)
    duration = librosa.get_duration(y=audio, sr=sample_rate)
    return audio.astype(np.float32), float(duration)

@app.get("/ping")
def ping():
    return JSONResponse(content="pong")

@app.post("/asr")
async def asr(file: UploadFile):

    # check if file type supported.
    if not file.filename.lower().endswith(SUPPORTED_FILE_FORMATS):
        raise HTTPException(status_code=400, detail="Unsupported file type. Upload an audio file.")
    
    # create a temporary directory to store the uploaded file.
    tmpdir = tempfile.mkdtemp(prefix="asr_")
    tmp_path = os.path.join(tmpdir, file.filename)
    
    # resample and transcribe the audio file.
    try:
        with open(tmp_path, "wb") as f:
            f.write(await file.read())

        audio, duration = resample_audio(tmp_path, SAMPLE_RATE)
        text = transcribe(audio)

        return {"transcription": text, "duration": f"{duration:.2f}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR failed: {e}")
    finally:
        try:
            # do clean up of created directory.
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
            os.rmdir(tmpdir)
        except Exception as e:
            pass

if __name__ == "__main__":
    uvicorn.run("asr_api:app", host="0.0.0.0", port=8001, reload=False)