from openai import OpenAI
from config import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

# Создаем ассистента без 'retrieval', но с поддерживаемыми инструментами
assistant = client.beta.assistants.create(
    name="Voice Assistant",
    model="gpt-4-turbo",
    instructions="Ты — голосовой помощник. Отвечай четко и кратко.",
    tools=[{"type": "code_interpreter"}, {"type": "file_search"}]  # Убрали 'retrieval'
)

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

async def ask_gpt(text: str, thread_id: str = None) -> str:
    """Отправляет текст в Assistants API и получает ответ."""
    
    # Создаем thread для хранения контекста, если его нет
    if thread_id is None:
        thread = client.beta.threads.create()
        thread_id = thread.id

    # Отправляем сообщение ассистенту
    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=text
    )

    # Запускаем ассистента
    run = client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant.id)

    # Ожидаем завершения работы ассистента
    while run.status in ["queued", "in_progress"]:
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)

    # Получаем ответ ассистента
    messages = client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value  # Возвращаем последний ответ ассистента
