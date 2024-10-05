import json
import logging
import re
import requests
import time

from dotenv import load_dotenv
from io import BytesIO
from openai import OpenAI
import os
from PIL import Image
from src.utils.mj import imagine, fetch
from src.utils.style import STYLE_MAP
from typing import Dict, List
from xml.etree import ElementTree

load_dotenv()

logging.basicConfig(filename='../../mj.log', level=logging.INFO, format='%(asctime)s - %(message)s')

API_KEY = os.getenv("MJ_KEY")
HOST_NAME = os.getenv("MJ_HOSTNAME")
MODEL = os.getenv("TEXT_MODEL")
KEY = os.getenv("TEXT_MODEL_KEY")
URL = os.getenv("TEXT_MODEL_URL")
HEADERS = {
    'Authorization': f'Bearer {API_KEY}',
    'User-Agent': 'MyPythonApp/1.0',
    'Content-Type': 'application/json'
}

PersonaInfo = Dict[str, str]
PersonaDict = Dict[str, PersonaInfo]


def load_banned_words(path):
    output = ""
    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            output += line.strip() + ", "
    return output


def replace_banned_words(text, path):
    with open(path, 'r') as file:
        replacements = json.load(file)

    words = re.split(r'(\W+)', text)
    new_words = []
    for word in words:
        lower_word = word.lower().strip()
        if lower_word in replacements:
            if word.isupper():
                new_words.append(replacements[lower_word].upper())
            elif word[0].isupper():
                new_words.append(replacements[lower_word].capitalize())
            else:
                new_words.append(replacements[lower_word])
        else:
            new_words.append(word)
    return ''.join(new_words)


def translate(description_zh):
    client = OpenAI(api_key=KEY, base_url=URL)
    messages = [
        {"role": "system",
         "content": f"Please translate the following content from Chinese to English directly without rephrasing or changing the structure. \nMaintain all original punctuation and formatting. If the task cannot be executed"},
        {"role": "user", "content": description_zh},
    ]
    try:
        response = client.chat.completions.create(model=MODEL, messages=messages, stream=True)
        output = ""
        for chunk in response:
            if chunk.choices != [] and chunk.choices[0].delta.content is not None:
                output += chunk.choices[0].delta.content
            else:
                break

        output = replace_banned_words(output, "../utils/replace.json")
        return output
    except Exception as e:
        print(f"An error occurred: {type(e).__name__}, {str(e)}")
        return None


def parse_personas(personas: List[str]) -> PersonaDict:
    personas_dict: PersonaDict = {}
    for persona in personas:
        name_match = re.search(r"name=(.*?),", persona)
        gender_match = re.search(r"gender=(.*?),", persona)
        age_match = re.search(r"age=(.*?),", persona)
        appearance_match = re.search(r"appearance=(.*)\)", persona)
        if name_match and gender_match and age_match and appearance_match:
            name = name_match.group(1).strip()
            gender = gender_match.group(1).strip()
            age = age_match.group(1).strip()
            appearance = appearance_match.group(1).strip()
            personas_dict[name] = {
                "gender": gender,
                "age": age,
                "appearance": appearance
            }
    return personas_dict


def parse_prompt(personas: List[str], style: str, play: str, ratio: str) -> str:
    play_xml = ElementTree.fromstring(play)
    perspective_map = {
        "近景": "close-up",
        "中景": "medium shot",
        "远景": "long shot"
    }
    direction_map = {
        "正拍": "front shot",
        "背拍": "back shot",
        "侧拍": "side shot"
    }
    distance_text = play_xml.find('play_distance').text.strip()
    direction_text = play_xml.find('play_direction').text.strip()
    perspective = f"{perspective_map.get(distance_text, 'unknown distance')}, {direction_map.get(direction_text, 'unknown direction')}"
    environment = play_xml.find('play_environment').text.strip()

    personas_dict = parse_personas(personas)
    play_roles_actions = play_xml.find('play_roles_actions').text
    for name, details in personas_dict.items():
        gender = details["gender"]
        age = details["age"]
        appearance = details["appearance"]
        enhanced_description = f"{name}({gender}, {age}, {appearance})"
        play_roles_actions = play_roles_actions.replace(name, enhanced_description, 1)

    style_info = STYLE_MAP.get(style, {})
    style_description = style_info.get("description", "")
    style_weight = f"--sw {style_info.get('weight', 0)}"
    style_images = style_info.get("image_url", [])
    sref_url = f"--sref {' '.join(style_images)}"
    parameters = f"{sref_url} {style_weight}"

    description_zh = f"{play_roles_actions}, {environment}"
    # print(description_zh)
    description_en = translate(description_zh)

    ratio = f"--ar {ratio}"
    video_element = f"{distance_text}, {direction_text}, {description_zh}"
    # print(video_element)

    final_prompt = f"{perspective}, {description_en}, {style_description} --no text, watermarks, black bars, border, canvas, matte, frame {parameters} {ratio} --v 6"
    print(final_prompt)

    return final_prompt


def generate_play_image(prompt):
    task_id = imagine(prompt)
    image_url = fetch(task_id)
    return image_url


def crop(image_url, region):
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    width, height = image.size
    single_width = width // 2
    single_height = height // 2
    if region == 1:
        left, top, right, bottom = 0, 0, single_width, single_height
    elif region == 2:
        left, top, right, bottom = single_width, 0, width, single_height
    elif region == 3:
        left, top, right, bottom = 0, single_height, single_width, height
    elif region == 4:
        left, top, right, bottom = single_width, single_height, width, height

    cropped_image = image.crop((left, top, right, bottom))
    cropped_image.show()
    return cropped_image


def get_play_image(personas, style, play, ratio):
    # trans_start = time.time()
    final_prompt = parse_prompt(personas, style, play, ratio)
    # print(f'Translate Duration: {time.time() - trans_start}')
    # gen_start = time.time()
    image_url = generate_play_image(final_prompt)
    # print(f'Generate Image: {time.time() - gen_start}')
    # crop_start = time.time()
    image = crop(image_url, 1)
    # print(f'Crop Duration: {time.time() - crop_start}')
    return image


def main():
    personas = [
        'Persona(name=陆老, gender=男, age=老年, appearance=衣着剪裁得体的唐装。 外观精神矍铄，身形挺拔，脸上布满岁月的痕迹，但一双鹰隼般的眸子依然炯炯有神，不怒自威。花白的头发梳得一丝不苟，露出饱经风霜的额头。)',
        'Persona(name=江薇, gender=女, age=青年, appearance=着干练的职业套装。 外观精致的妆容，眉宇间透着一股英气，干练的短发，显得精明能干。)',
        'Persona(name=陆豪, gender=男, age=青年, appearance=wearing a black shirt。 身材精瘦，但充满力量。)',
        'Persona(name=黄丽丽, gender=女, age=青年, appearance=wearing a red dress. Long straight hair, heavy makeup, dressed in a glamorous and alluring way, with a charming figure)',
        'Persona(name=万少, gender=男, age=青年, appearance=wearing a yellow hawaiian shirt;. His appearance is overly flashy and tacky, with a fat figure, a sturdy gold chain around his neck, and rings all over his hands, dressed like a nouveau riche.)',
    ]
    style = "国风动漫"
    play = """
    <play id="1">
        <play_roles>陆老</play_roles>
        <play_roles_actions>
        陆老，走向江薇，表情平静。\n江薇，站在原地，手持文件夹，表情恭敬。
        </play_roles_actions>
        <play_environment>私人机场停机坪：铺着红色地毯，停放着豪华直升机，阳光强烈</play_environment>
        <play_distance>中景</play_distance>
        <play_direction>正拍</play_direction>
    </play>
    """
    ratio = "16:9"
    parse_prompt(personas, style, play, ratio)
    get_play_image(personas, style, play, ratio)


if __name__ == '__main__':
    main()
