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
from typing import Dict, List, Any

from src.utils.mj import imagine, fetch
from src.utils.style import STYLE_MAP

load_dotenv()

# Obtain a logger for this module
logger = logging.getLogger(__name__)

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

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the path to replace.json relative to the script directory
replace_json_path = os.path.join(script_dir, '..', 'utils', 'replace.json')

# Define additional banned words for sanitization
ADDITIONAL_BANNED_WORDS = [
    # ... [List of banned words as in your original code] ...
]


def replace_banned_words(text):
    try:
        with open(replace_json_path, 'r', encoding='utf-8') as file:
            replacements = json.load(file)
    except FileNotFoundError:
        logger.error(f"replace.json not found at {replace_json_path}")
        return text
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding replace.json: {e}")
        return text

    # Sort banned words by length in descending order to replace longer phrases first
    sorted_replacements = sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True)

    for banned_word, replacement in sorted_replacements:
        # Use word boundaries for exact matching and case-insensitive replacement
        pattern = re.compile(r'\b{}\b'.format(re.escape(banned_word)), re.IGNORECASE)
        text = pattern.sub(replacement, text)

    logger.debug("Banned words replaced in text.")
    return text


def sanitize_final_prompt(text):
    """
    Removes or replaces any remaining banned words in the final prompt.
    """
    for word in ADDITIONAL_BANNED_WORDS:
        pattern = re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE)
        text = pattern.sub('[REDACTED]', text)
    logger.debug("Final prompt sanitized.")
    return text


def sanitize_translated_content(text):
    """
    Removes or replaces banned patterns in the translated text.
    """
    for word in ADDITIONAL_BANNED_WORDS:
        regex = re.compile(r'\b{}\b'.format(re.escape(word)), re.IGNORECASE)
        text = regex.sub('[REDACTED]', text)
    logger.debug("Translated content sanitized.")
    return text


def translate(description_zh):
    client = OpenAI(api_key=KEY, base_url=URL)
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that translates Chinese text to English. "
                "Translate the content directly without adding any additional information. "
                "Ensure that the translation is safe, respectful, and adheres to community standards. "
                "Avoid explicit content, violence, hate speech, and culturally insensitive material. "
                "Do not respond with messages like 'sorry, your content is sensitive' or similar refusals."
            ),
        },
        {"role": "user", "content": description_zh},
    ]
    try:
        response = client.chat.completions.create(model=MODEL, messages=messages, stream=True)
        output = ""
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                output += chunk.choices[0].delta.content
        output = replace_banned_words(output)
        output = sanitize_translated_content(output)  # Sanitize after translation

        logger.info("Translation completed.")
        return output
    except Exception as e:
        logger.error(f"An error occurred during translation: {type(e).__name__}, {str(e)}")
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
    logger.debug("Personas parsed successfully.")
    return personas_dict


def parse_prompt(personas: List[str], style: str, play: Dict[str, Any], ratio: str) -> str:
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
    distance_text = play.get('play_distance', '').strip()
    direction_text = play.get('play_direction', '').strip()
    perspective = f"{perspective_map.get(distance_text, 'unknown distance')}, {direction_map.get(direction_text, 'unknown direction')}"
    environment = play.get('play_environment', '').strip()

    personas_dict = parse_personas(personas)
    play_roles_actions = play.get('play_roles_actions', '')
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
    sref_url = f"--sref {' '.join(style_images)}" if style_images else ""
    parameters = f"{sref_url} {style_weight}"

    description_zh = f"{play_roles_actions}, {environment}"
    description_en = translate(description_zh)

    # If translation failed, handle gracefully
    if not description_en:
        description_en = "Description unavailable."

    # Create the final prompt
    final_prompt = f"{perspective}, {description_en}, {style_description} --no text, watermarks, black bars, border, canvas, matte, frame {parameters} --ar {ratio} --v 6"

    # Sanitize the final prompt
    final_prompt = sanitize_final_prompt(final_prompt)

    # Log the final prompt
    logger.info(f"Play ID: {play.get('id')}\nFinal Prompt: {final_prompt}")

    print("Final Prompt:", final_prompt)

    return final_prompt


def generate_play_image(prompt):
    task_id = imagine(prompt)
    image_url = fetch(task_id)
    logger.info(f"Image generated for prompt: {prompt}")
    return image_url


def get_play_image(personas, style, play, ratio, max_retries=2):
    for attempt in range(max_retries):
        final_prompt = parse_prompt(personas, style, play, ratio)
        image_url = generate_play_image(final_prompt)

        # Check if image_url contains a failure reason
        if image_url and "failreason" not in image_url.lower():
            logger.info(f"Image URL retrieved successfully: {image_url}")
            return image_url
        else:
            logger.warning(f"Attempt {attempt + 1} failed for Play ID {play.get('id')}. Retrying...")
            time.sleep(2)  # Wait before retrying
    logger.error(f"All attempts failed for Play ID {play.get('id')}. Skipping this play.")
    return None


def crop(image_url, region):
    try:
        response = requests.get(image_url)
        response.raise_for_status()
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
        else:
            logger.warning(f"Invalid region: {region}. Skipping cropping.")
            return image

        cropped_image = image.crop((left, top, right, bottom))
        cropped_image.show()
        logger.info(f"Image cropped for region {region}.")
        return cropped_image
    except Exception as e:
        logger.error(f"Error cropping image: {e}")
        return None


def main():
    # Sample personas list (as in results.json)
    personas = [
        'Persona(name=陆老, gender=男, age=老年, appearance=衣着剪裁得体的唐装。 外观精神矍铄，身形挺拔，脸上布满岁月的痕迹，但一双鹰隼般的眸子依然炯炯有神，不怒自威。花白的头发梳得一丝不苟，露出饱经风霜的额头。)',
        'Persona(name=江薇, gender=女, age=青年, appearance=着干练的职业套装。 外观精致的妆容，眉宇间透着一股英气，干练的短发，显得精明能干。)',
        'Persona(name=陆豪, gender=男, age=青年, appearance=穿着黑色衬衫。 身材精瘦，但充满力量。)',
        'Persona(name=黄丽丽, gender=女, age=青年, appearance=穿着红色连衣裙。长直发，浓妆艳抹，打扮得妖艳动人，身材妩媚)',
        'Persona(name=万少, gender=男, age=青年, appearance=穿着黄色夏威夷衬衫；外表过于浮夸俗气，身材肥胖，脖子上挂着粗大的金链子，手上戴满戒指，打扮得像个暴发户。)'
    ]

    # Sample plays list in the format of results.json
    plays = [
        {
            "id": "1",
            "play_roles": "陆老, 江薇",
            "play_roles_actions": "陆老，走向江薇，表情平静。\n江薇，站在原地，手持文件夹，表情恭敬。",
            "play_environment": "私人机场停机坪：铺着红色地毯，停放着豪华直升机，阳光强烈",
            "play_distance": "中景",
            "play_direction": "正拍"
        },
        {
            "id": "2",
            "play_roles": "陆豪, 黄丽丽",
            "play_roles_actions": "陆豪，靠在墙边，表情冷漠。\n黄丽丽，走过陆豪身边，表情挑衅。",
            "play_environment": "豪华酒店大堂：水晶吊灯闪耀，大理石地面反射光泽，奢华气息浓厚",
            "play_distance": "近景",
            "play_direction": "侧拍"
        }
        # Add more plays as needed
    ]

    style = "国风动漫"
    ratio = "16:9"

    image_urls = []

    for play in plays[:5]:  # Process only the first 5 plays
        final_prompt = parse_prompt(personas, style, play, ratio)
        image_url = get_play_image(personas, style, play, ratio)
        if image_url:
            print("Generated Image URL:", image_url)
            image_urls.append(image_url)
        else:
            print(f"Failed to generate image for play ID {play['id']}")
            image_urls.append(None)


if __name__ == '__main__':
    main()
