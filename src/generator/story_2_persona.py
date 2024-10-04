import asyncio
import aiofiles
import os
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from openai import AsyncOpenAI
from src.utils.chat import chat

load_dotenv()

MODEL = os.getenv("TEXT_MODEL")
KEY = os.getenv("TEXT_MODEL_KEY")
URL = os.getenv("TEXT_MODEL_URL")

CLIENT = AsyncOpenAI(api_key=KEY, base_url=URL)

SYSTEM_PROMPT_story_2_persona = """
你是一位经验丰富的小说编辑。我将为你提供一章小说故事，请你从中精读并识别所有关键角色及其特征。

---
任务要求：
- 请根据章节内容，为每个实际参与情节的角色创建一个角色卡片。
- 对于第一人称小说，请使用叙述中的称呼，主角自己就用"主人公"作为角色名称。对于第三人称小说，请使用角色在故事中的名字。不要返回未知。
- 使用以下格式，并为每个角色使用一个独立的<persona>标签。

```xml
<persona>
    <persona_name>角色名称，全名</persona_name>
    <persona_gender>角色性别</persona_gender>
    <persona_age>从以下选项中选择一个最合适的描述角色年龄：儿童, 少年, 青年, 中年, 老年, 未知</persona_age>
    <persona_appearance>基于情节推测联想扩写，生成一个详细的外形描述，不少于20字。返回的内容中只需要提到外貌相关的内容，不要通过解释型内容来描述外貌。不能返回未知。例如：“方形脸，戴圆框金丝眼镜，微胖，年纪较大，脸上有一些褶皱，黑发中混着一些白发，中国人，稍微有点驼背，”如果文中没有具体描述，则生成外观描述。不能返回未知。</persona_appearance>
    <persona_dress>基于情节推测联想和扩写角色服装，不少于10字。例如“上半身酒红色的传统唐装，下半身中山裤子。”或者“一顶绿色的遮阳帽，一双水晶高跟鞋，白色的休闲装。”。返回的是形容词和名词的形式，不要包含解释型描述。结尾是句号。如果文中没有具体描述，则自动生成一个服装。不能返回未知。</persona_dress>
</persona>
```

---
注意事项：
- 请仅为在故事中具有实际行动或明显影响情节进展的角色生成角色卡片。如果角色仅在对话中被提及而没有任何实际行动或对话，那么不需要为该角色创建角色卡片。这样做是为了确保每个角色都对故事的发展有直接的贡献
- 确保每个描述都是信息丰富和具体的，以便更好地了解角色。
"""


class Persona:
    def __init__(self, name, gender, age, appearance, dress):
        self.name = name
        self.gender = gender
        self.age = age
        self.appearance = appearance
        self.dress = dress


async def parse_personas(xml_personas):
    root = ET.fromstring(f"<personas>{xml_personas}</personas>")
    descriptions = []
    for persona_elem in root.findall('persona'):
        name = persona_elem.find('persona_name').text
        gender = persona_elem.find('persona_gender').text
        age = persona_elem.find('persona_age').text
        appearance = persona_elem.find('persona_appearance').text
        dress = persona_elem.find('persona_dress').text
        persona = Persona(name, gender, age, appearance, dress)
        discription = f"Persona(name={persona.name}, gender={persona.gender}, age={persona.age}, appearance=衣着{persona.dress} 外观{persona.appearance})"
        descriptions.append(discription)
    return descriptions


async def read_chapter_file(filename):
    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        content = await file.read()
        # print("Read content:", content[:100])
        return content


async def generate_persona(story_content):
    prompt = SYSTEM_PROMPT_story_2_persona
    response = await chat(prompt, story_content, MODEL)
    return response


async def get_persona(story_content):
    xml_personas = await generate_persona(story_content)
    if xml_personas:
        personas = await parse_personas(xml_personas)
        print("Generated Personas:", personas)
        return personas
    else:
        print("No persona could be generated.")
        return None


async def main():
    story_content = await read_chapter_file("../data/huanghou.txt")
    await get_persona(story_content)


if __name__ == '__main__':
    asyncio.run(main())
