import asyncio
from src.utils.utils import read_story, save_file, read_results
from src.generator.story_2_persona import get_persona, extract_cast
from src.generator.story_2_frag import get_fragments
from src.generator.frag_2_play import get_plays
from src.generator.play_2_image import get_play_image


async def main():
    output_file = "data/output/results.json"
    results = {}

    # # 1. import story contents
    # story_content = await read_story("data/processed/ch1-4.txt")
    # save_file(story_content, "story_content", output_file)
    # print(story_content)

    # # # 2. generate personas
    # personas = await get_persona(story_content)
    # cast = extract_cast(personas)
    # save_file(personas, "personas", output_file)
    # save_file(cast, "cast", output_file)
    # print(cast)
    # print(personas)

    # 3. generate fragmentsc
    # fragments = await get_fragments(story_content)
    # save_file(fragments, "fragments", output_file)
    # print(fragments)

    # # 4. generate plays
    fragments = str(read_results("fragments", output_file)).replace("\n", "")
    cast = read_results("cast", output_file)

    plays = await get_plays(fragments, cast)
    save_file(plays, "plays", output_file)
    print(plays)

    # # 5. generate images
    # ratio = "16:9"
    # style = "国风动漫"
    # for play in plays:
    #     image = get_play_image(personas, style, play, ratio)


if __name__ == "__main__":
    asyncio.run(main())
