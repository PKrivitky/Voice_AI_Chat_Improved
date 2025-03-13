from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

async def stt(audio_path: str) -> str:
    """Преобразует голос в текст через OpenAI Whisper."""
    with open(audio_path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return transcription.text

async def tts(text: str, output_path: str):
    """Генерирует голосовой ответ через OpenAI TTS."""
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    with open(output_path, "wb") as f:
        f.write(response.content)

async def ask_gpt(text: str) -> str:
    """Отправляет текст в GPT-4 и получает ответ."""
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": text}]
    )
    return response.choices[0].message.content
