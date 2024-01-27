import requests
from config import catalog_id, secret_key
import json


def _get_response_yandex_gpt(details: dict):
    sex = details["sex"]
    age = details["age"]
    salary = details["salary"]
    all_cost = details["all_cost"]
    main_category = details["main_category"]
    where_live = details["where_live"]
    hobbies = ", ".join(details["hobbies"])
    prompt_gpt = f"Привет, Финанс! Поскажи мне, грамотно ли я трачу свои деньги,\
за этот месяц я потратил {all_cost} рублей.\
Я {sex} {age} лет, зарабатываю {salary} рублей. Пока что я {where_live}\
квартиру.\
Люблю {hobbies} хобби. В основном трачу на {main_category}.\
 Не нужно здороваться и представляться"
    prompt = {
        "modelUri": f"gpt://{catalog_id}/yandexgpt-lite",
        "completionOptions": {"stream": False, "temperature": 0.6, "maxTokens": "200"},
        "messages": [
            {
                "role": "system",
                "text": "Ты финансовый асистент Финанс, который дают советы людям,\
как тратить их деньги",
            },
            {
                "role": "user",
                "text": prompt_gpt,
            },
        ],
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {secret_key}",
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    json_data = json.loads(result)
    return json_data["result"]["alternatives"][0]["message"]["text"], prompt_gpt


if __name__ == "__main__":
    details = {
        "age": 20,
        "sex": "Мужчина",
        "salary": 80000,
        "hobbies": "Спокойные",
        "where_live": "Неснимает",
        "all_cost": 50_000,
        "main_category": "жилье",
    }
    result = _get_response_yandex_gpt(details)
    print(result)
