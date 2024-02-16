import g4f


def gpt_3_answer(prompt):
    response = g4f.ChatCompletion.create(
        model=g4f.models.gpt_35_turbo,
        messages=[
            {
                "role": "system",
                "content": """Ты финансовый ассистент.\
                Давай лаконичные и быстрые ответы на русском языке""",
            },
            {"role": "user", "content": "Что посоветуешь мне купить сегодня?"},
            {"role": "assistant", "content": "Подскажите свой бюджет"},
            {"role": "user", "content": "Около 30 тысяч рублей"},
        ],
        stream=False,
    )
    return response
