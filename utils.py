from openai import AsyncOpenAI
from config import settings
from database import AsyncSessionLocal, UserSession, UserValue
from validations import validate_value
import json
import logging
import os
from sqlalchemy import select

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
logger = logging.getLogger(__name__)

async def stt(audio_path: str) -> str:
    """Преобразует голос в текст через OpenAI Whisper."""
    try:
        if not os.path.exists(audio_path):
            logging.error(f"Файл {audio_path} не найден")
            return ""

        with open(audio_path, "rb") as audio_file:
            transcription = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return transcription.text

    except Exception as e:
        logging.error(f"STT error: {str(e)}")
        return ""

async def tts(text: str, output_path: str) -> bool:
    """Генерирует голосовой ответ. Возвращает True при успехе."""
    try:
        if not text:
            return False
            
        response = await client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        with open(output_path, "wb") as f:
            f.write(response.content)
        if os.path.exists(output_path):
            return True
        else:
            logger.error("Файл не был создан")
            return False
    except Exception as e:
        await print(f'Ошибка при распознавании: {e}')

async def initialize_user_session(user_id: int) -> str:
    """Создает или возвращает существующий thread_id."""
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(
                select(UserSession).where(UserSession.user_id == user_id)
            )
            session_obj = result.scalar_one_or_none()
            
            if session_obj:
                return session_obj.thread_id

            thread = await client.beta.threads.create()
            new_session = UserSession(user_id=user_id, thread_id=thread.id)
            db.add(new_session)
            await db.commit()
            return thread.id
            
        except Exception as e:
            await db.rollback()
            logging.error(f"Ошибка инициализации сессии: {e}")
            raise

async def process_assistant_response(run, thread_id: str, user_id: int):
    """Обрабатывает вызовы функций ассистента."""
    outputs = []

    for tool_call in run.required_action.submit_tool_outputs.tool_calls:
        if tool_call.function.name == "save_value":
            args = json.loads(tool_call.function.arguments)
            value = args.get("value", "")
            logging.info(f"Получено значение от OpenAI: {value})")
            
            if await validate_value(value):
                async with AsyncSessionLocal() as session:
                    session.add(UserValue(user_id=user_id, value=value))
                    await session.commit()
                    logger.info(f"Сохранено значение: {value}")
                outputs.append({"tool_call_id": tool_call.id, "output": "success"})
            else:
                outputs.append({"tool_call_id": tool_call.id, "output": "invalid_value"})
    
    if outputs:
        await client.beta.threads.runs.submit_tool_outputs(
            thread_id=thread_id,
            run_id=run.id,
            tool_outputs=outputs
        )

async def ask_gpt(user_id: int, text: str, assistant_id: str) -> str:
    """Использует существующего ассистента."""
    thread_id = await initialize_user_session(user_id)
    
    await client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=text
    )
    
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread_id,
        assistant_id=assistant_id
    )
    
    if run.status == "requires_action":
        await process_assistant_response(run, thread_id, user_id)
    
    messages = await client.beta.threads.messages.list(thread_id=thread_id)
    return messages.data[0].content[0].text.value