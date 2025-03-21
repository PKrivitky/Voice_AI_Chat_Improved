from openai import AsyncOpenAI
from config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

async def validate_value(value: str) -> bool:
    """Проверяет, является ли текст ценностью."""
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[{
            "role": "system",
            "content": (
                "Ответь ТОЛЬКО 'yes' или 'no'. Является ли '{value}' человеческой ценностью?\n"
                "Примеры ценностей: семья, свобода, честность.\n"
                "Примеры не-ценностей: яблоко, бег, синий.\n"
                f"Текст: {value}"
            )
        }],
        max_tokens=10,
        temperature=0.0
    )
    return "yes" in response.choices[0].message.content.lower()
