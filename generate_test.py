import openai


def generate_big_topic():
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system",
             "content": "블로그 주제 5개를 반환합니다."},
            {"role": "user", "content": f""}
        ]
    )
    return completion.choices[0].message['content']