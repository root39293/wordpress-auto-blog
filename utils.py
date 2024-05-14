from openai import OpenAI
import requests

def generate_content(topic, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "You are now a power blogger. Your role is to write a blog post related to the topic the user requests. You should only write the main content of the blog post. Do not include any other sections. Write as detailed and as lengthy as possible."
            },
            {
                "role": "user",
                "content": f"The topic is {topic}. Please write a blog post about {topic}."
            }
        ]
    )
    return response.choices[0].message.content

def generate_topics(topic, count, api_key):
    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are now responsible for generating blog topics. Generate concise and essential blog post titles for the given broad topic. Separate each title with a newline. Provide {count} titles."
                },
                {
                    "role": "user",
                    "content": f"Please generate {count} blog topics for {topic}."
                }
            ]
        )
        topics_str = response.choices[0].message.content
        topics_list = [
            topic.replace('"', "").strip()
            for topic in topics_str.split("\n")
            if topic.strip()
        ]

        entire_topic_list = []
        for topic in topics_list:
            topic_parts = topic.split(". ")
            if len(topic_parts) > 1:
                topic_without_number = topic_parts[1]
            else:
                topic_without_number = topic_parts[0]

            topic_without_extra_symbols = topic_without_number.split("-")[0].split(":")[0]
            entire_topic_list.append(topic_without_extra_symbols)

        return entire_topic_list
    except Exception as e:
        return str(e)

def create_wordpress_post(topic, content, username, password, wp_url):
    image_url = f"https://source.unsplash.com/featured/?{topic}"

    wordpress_url = wp_url + "/wp-json/wp/v2/posts"

    headers = {
        "Content-Type": "application/json",
    }

    data = {
        "title": topic,
        "content": f'<img src="{image_url}">\n\n{content}',
        "status": "publish",
    }

    response = requests.post(
        wordpress_url, headers=headers, json=data, auth=(username, password)
    )
    response.raise_for_status()
