import asyncio
from src.utils.utils import read_file
from src.generator.story_2_persona import get_persona, extract_cast
from src.generator.story_2_frag import get_fragments
from src.generator.frag_2_play import get_plays
from src.generator.play_2_image import get_play_image


async def main():
    # 1. import story contents
    story_content = await read_file("data/processed/ch1-4.txt")
    print(story_content)

    # 2. generate personas
    personas = await get_persona(story_content)
    cast = extract_cast(personas)
    print(cast)
    print(personas)

    #
    # # 3. generate fragments
    # fragments = await get_fragments(story_content)
    #
    # # 4. generate plays
    # plays = await get_plays(fragments, cast)
    #
    # # 5. generate images
    # ratio = "16:9"
    # style = "国风动漫"
    # for play in plays:
    #     image = get_play_image(personas, style, play, ratio)


if __name__ == "__main__":
    asyncio.run(main())
