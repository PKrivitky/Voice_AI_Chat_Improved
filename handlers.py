import os
import time
from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from openai import AsyncOpenAI
from config import settings
from utils import stt, tts, ask_gpt
from database import AsyncSessionLocal, UserSession
from sqlalchemy import select, delete

router = Router()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

@router.message(CommandStart())
async def process_start_command(message: Message):
    user_id = message.from_user.id
    async with AsyncSessionLocal() as db:
        try:
            await db.execute(
                    delete(UserSession).where(UserSession.user_id == user_id)
                )
            await db.commit()
            result = await db.execute(
                select(UserSession).where(UserSession.user_id == user_id)
            )
            session_obj = result.scalar_one_or_none()
            
            if session_obj:
                await message.answer("Сессия уже начата! Продолжаем общение.")
                return

            thread = await client.beta.threads.create()
            new_session = UserSession(user_id=user_id, thread_id=thread.id)
            db.add(new_session)
            await db.commit()
            
            initial_prompt = "Привет! Расскажи, что для тебя важно в жизни?"
            await message.answer(initial_prompt)
            
            await client.beta.threads.messages.create(
                thread_id=thread.id,
                role="assistant",
                content=initial_prompt
            )

        except Exception as e:
            await db.rollback()
            print(f"Ошибка при старте сессии: {e}")
            await message.answer("Произошла ошибка. Попробуйте позже.")
        finally:
            if db:
                await db.close()

@router.message()
async def handle_voice_message(message: Message, **kwargs):
    bot = kwargs['bot']
    user_id = message.from_user.id
    response_audio = None
    unique_name = f"{int(time.time())}.ogg"

    try:
        file = await bot.get_file(message.voice.file_id)
        await bot.download_file(file.file_path, unique_name)
        
        speech_text = await stt(unique_name)
        if not speech_text:
            await message.reply("Не удалось распознать речь")
            return

        assistant_id = settings.ASSISTANT_ID
        
        gpt_answer = await ask_gpt(user_id, speech_text, assistant_id)
        
        response_audio = f"response_{int(time.time())}.ogg"
        result = await tts(gpt_answer, response_audio)
        print(f"Внимание!!!!! - {result}")
        if result:
            await message.reply_voice(FSInputFile(response_audio))
        else:
            await message.reply("Ошибка генерации ответа")

    except Exception as e:
        await message.reply(f"Ошибка: {str(e)}")
    
    finally:
        files = [unique_name]
        if response_audio and os.path.exists(response_audio):
            files.append(response_audio)
        for file in files:
            try:
                os.remove(file)
            except Exception as e:
                print(f"Ошибка удаления файла {file}: {e}")

def register_handlers(dp):
    dp.include_router(router)