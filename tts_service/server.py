from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import torchaudio
import uvicorn
from dio_tts import load_model, synthes_speech

app = FastAPI()
@app.on_event("startup")
async def startup():
    load_model()

class TTSRequest(BaseModel):
    text: str

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    try:
        audio = synthes_speech(request.text)

        # Сохраняем как в тесте
        output_path = "dio_output.wav"
        torchaudio.save(output_path,
                        audio.unsqueeze(0).cpu(),
                        24000)

        # Читаем файл и отдаём
        with open(output_path, "rb") as f:
            audio_data = f.read()

        return Response(content=audio_data, media_type="audio/wav")

    except Exception as e:
        print(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)