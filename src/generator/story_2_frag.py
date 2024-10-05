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


# # FOR LONG CONTENT CHAPTER STORIES SPECIFIC: Story-->Outline-->Frags
# SYSTEM_PROMPT_story_to_outline = """
# 你是一位经验丰富的分镜大师。请根据我提供的一章完整小说故事，将其拆解为n个分镜，确保每个分镜既引人入胜又设计精良。为每个分镜提供简短的大纲，以便后续可以根据这些大纲快速定位到对应的原文段落。返回的结果应该使用以下XML格式：
# ```xml
# <outlines>
#     <outline id="1">...</outline>
#     <outline id="2">...</outline>
#     ...
#     <outline id="n">...</outline>
# </outlines>
# """

# SYSTEM_PROMPT_prompt_story_to_frags = """
# 你是一位经验丰富的小说段落拆分大师。我将向你提供一份小说的分镜大纲，其中包含了多个带有独立ID的条目。每个条目都代表原文中的一个特定段落或段落组。请你根据这个大纲精确地从原文中提取对应的段落，并确保不遗漏任何内容。分镜大纲中有多少条目，你就需要拆分成相应数量的段落。请将所有提取的内容按照分镜大纲的ID以以下XML格式返回：
# ```xml
# <fragments>
#     <frag id="1">outline id=1 对应原文中相关的段落</frag>
#     ...
#     <frag id="n">outline id=n 对应原文中相关的段落</frag>
# </fragments>
# ```
# """


def gen_prompts(story_content):
    print(f'Len: {len(story_content)}')
    content_len = len(story_content)
    if content_len >= 5000:
        m = 5
    elif content_len > 4000:
        m = 4
    else:
        m = 3
    print(m)

    prompt_story_2_frags = f"""
你是一位经验丰富的小说分镜大师。我将为你提供一篇小说的原文，请你把它拆分成n个分镜。确保每个分镜既引人入胜又设计精良，并且要涵盖原文的全部内容。这样做能帮助我们更好地理解和展示小说的故事结构。

---任务要求
- 请以大约{m}句话的原文内容来定义每个分镜。
- 你只需要返回带有id的原文内容，不需要返回任何你对分镜的分析和其他与原文无关的内容。
- 使用以下XML格式来展示所有分镜和它们对应的原文内容，确保格式准确无误。
```xml
<frag id="1">大约原文中的{m}句话左右</frag>
...
<frag id="n">大约原文中的{m}句话左右</frag>
```
"""
    return prompt_story_2_frags


async def read_chapter_file(filename):
    # TODO: Separate original contents to separate parts and store then process to persona and frags
    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        content = await file.read()
        return content


def process_buffer(buffer):
    new_buffer = buffer
    while '</frag>' in new_buffer:
        last_frag_end = new_buffer.find('</frag>') + len('</frag>')
        fragment_xml = new_buffer[:last_frag_end]
        cleaned_xml = fragment_xml.strip().strip("```").strip("xml").strip()
        new_buffer = new_buffer[last_frag_end:]

        try:
            root = ET.fromstring(f'<data>{cleaned_xml}</data>')
            for frag in root.findall('frag'):
                frag_id = frag.attrib.get('id')
                text_content = (frag.text or "").strip()
                print(f"Fragment {frag_id}: {text_content}")
        except ET.ParseError as e:
            print("Error parsing XML:", e)
            print("Faulty XML content:", cleaned_xml)
            continue

    return new_buffer


async def generate_content(story_content, system_prompt):
    messages = [
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": story_content
        }
    ]
    try:
        response = await CLIENT.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.6,
            stream=True
        )
        buffer = ""
        async for chunk in response:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                buffer += chunk.choices[0].delta.content
                buffer = process_buffer(buffer)
    except Exception as e:
        print(f"An error occurred: {type(e).__name__}, {str(e)}")
        return None


async def get_fragments(story_content):
    prompt_story_2_frags = gen_prompts(story_content)
    await generate_content(story_content, prompt_story_2_frags)
    # # Following codes for long content chapter separating
    # if outline:
    #     fragments = await generate_content(story_content, SYSTEM_PROMPT_prompt_story_to_frags + outline)
    #     # print(fragments)
    #     return fragments


async def main():
    story_content = await read_chapter_file(
        "../data/huanghou.txt")
    await get_fragments(story_content)


if __name__ == "__main__":
    asyncio.run(main())
