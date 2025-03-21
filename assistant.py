from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

ASSISTANT_INSTRUCTIONS = """
Ты — психолог-бот. Алгоритм:
1. Задавай уточняющие вопросы для выявления ценностей.
2. При первом упоминании ценности вызывай функцию `save_value`.
3. Подтверждай сохранение фразой: "Сохранил твою ценность: {value}".

Примеры:
- Пользователь: "Важна семья" → Вызываешь save_value("семья") → Ответ: "Ценность 'семья' сохранена!"
- Пользователь: "Люблю спорт" → Не ценность → Уточняй: "Что именно тебе нравится в спорте?"
"""

async def create_assistant():
    """Создаёт и кеширует ассистента OpenAI."""
    return await client.beta.assistants.create(
        name="Values Assistant",
        model="gpt-4o",
        instructions=ASSISTANT_INSTRUCTIONS,
        tools=[{
            "type": "function",
            "function": {
                "name": "save_value",
                "description": "Сохраняет выявленную ценность пользователя",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "value": {"type": "string", "description": "Ценность пользователя"}
                    },
                    "required": ["value"]
                }
            }
        }]
    )
