from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

async def create_assistant():
    return await client.beta.assistants.create(
        name="Voice Assistant",
        model="gpt-4o",
        instructions="Ты — голосовой помощник. Тебе надо узнать ценности пользователя.",
        tools=[{"type": "code_interpreter"}, {"type": "file_search"}]
    )

async def stt(audio_path: str) -> str:
    """Преобразует голос в текст через OpenAI Whisper."""
    try:
        with open(audio_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text
    except Exception as e:
        await print(f"Ошибка при распознавании: {e}")
        return

async def tts(text: str, output_path: str):
    """Генерирует голосовой ответ через OpenAI TTS."""
    try:
        response =  await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        with open(output_path, "wb") as f:
            f.write(response.content)
    except Exception as e:
        await print(f'Ошибка при распознавании: {e}')

async def ask_gpt(text: str, thread_id: str = None) -> str:
    """Отправляет текст в Assistants API и получает ответ."""
    
    # Создаем thread для хранения контекста, если его нет
    if thread_id is None:
        thread = await client.beta.threads.create()
        thread_id = thread.id

    # Отправляем сообщение ассистенту
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=text
    )

    # Запускаем ассистента
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=(await create_assistant()).id
    )

    if run.status == 'completed':
        message = await client.beta.threads.messages.list(thread_id=thread_id)
        return message.data[0].content[0].text.value
    else:
        return "Ошибка: Ассистент не смог обработать запрос."
    


    