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


async def read_chapter_file(filename):
    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        content = await file.read()
        return content


def generated_prompts(personas_name):
    personas_str = ", ".join(personas_name)

    prompt_frags_2_plays = f"""
    你是一位经验丰富的分镜师。本任务中，你需要根据我提供的片段内容，创作出相应的剧本分镜。

    片段的格式如下，每个片段编号与对应的剧本分镜编号一一对应：
    <fragments>
        <frag id="1">原文内容</frag>
        ...
        <frag id="n">原文内容</frag>
    </fragments>

    下述<play_roles>必须是出现在{{{personas_str}}}里面的角色。

    任务要求：
    - 为每个Fragment创建一个独立的<play>标签，格式如下：
    <plays>
        <play id="id">
            <play_roles>角色1, 角色2</play_roles>
            <play_roles_actions>
                使用第三人称形式，按“角色名称，动作，位置，表情”结构描述每个角色,不超过10个字。保持连续剧本（前后id）之间角色动作的一致性，如果角色在连续场景中动作未变，重复使用上一场景中的动作描述。避免使用过于抽象或含糊的表达，而是要具体明确，例如：“角色1，站在窗边，低着头，表情严肃。角色2，坐在沙发上，拿着书，表情认真。”即使原文中未明确指出，也应基于已有信息进行合理的推测和创造。不使用角色的台词来进行角色描述。
            </play_roles_actions>
            <play_environment>
                使用第三人称形式，详细且标准化地描述环境设置。环境描述应与前一剧本分镜保持一致，且格式统一，如“环境名称+具体特征”，可以适当增加或变更细节以反映时间的推移或故事背景的变化。例如：“书房：有四个红木书架，有一张塑料桌子和两把橡木椅子，光线昏暗；花园：有很多向日葵，立着两把铁锹，鹅卵石铺着的小路，远处一个稻草人”考虑画面构图，描述应帮助构建一个完整且具有吸引力的视觉画面。即使原文中未明确指出，也应基于已有信息进行合理的推测和创造。维持对应环境描述的连续性，确保信息的完整性。避免使用角色动作来描述环境。
            </play_environment>
            <play_distance>
                拍摄距离选择：近景、中景或远景
            </play_distance>
            <play_direction>
                拍摄角度选择：正拍、侧拍或背拍
            </play_direction>
        </play>
        <!-- 根据需要继续添加play，直至完成n个 -->
    </plays>
    - 必须生成完整的n个play，并确保输出的内容仅包含plays相关的XML格式数据。
    """

    return prompt_frags_2_plays


async def get_plays(fragments, personas_name):
    system_prompt = generated_prompts(personas_name)
    plays = await chat(system_prompt, fragments, MODEL)
    if plays:
        print("Generated Plays:", plays)
        return plays
    else:
        print("No plays could be generated.")
        return None


async def main():
    fragments = """
    <fragments>
    <frag id="1">我带女友回山区老家参加堂弟婚礼。堂弟说伴娘不够，请我女友凑个数。婚礼那天，堂弟带着女友去接亲后，却没再回来。</frag>
    <frag id="2">等我疯了一般冲到新娘家。发现女友衣衫不整，已经被新娘那个有小儿麻痹症的弟弟侮辱了。新娘一家还振振有词地说。</frag>
    <frag id="3">「反正女娃子都已经是破鞋了。「留在村里就别回去了，嫁给我儿子，刚好亲上加亲。」我这才知道，为了结婚，堂弟跟新娘一家约定要换亲。</frag>
    <frag id="4">他们竟把我女友，当成了彩礼的一部分！我怒不可遏，当即就要报警。却被新娘父母联合村民活活打死，抛尸荒野，被野狗吞噬入腹。</frag>
    <frag id="5">我的女友，被关在村子，饱受折磨，沦为生育工具。再睁眼，我重生到刚回山村那天。堂弟正一脸谄媚地看着我：「哥，把嫂子借我当个伴娘呗？」</frag>
</fragments>
    """
    personas_name = ["主人公", "堂弟", "陈婷婷"]
    await get_plays(fragments, personas_name)



if __name__ == "__main__":
    asyncio.run(main())
