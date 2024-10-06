import asyncio
import logging
import os

from src.utils.logger import setup_logging
from src.utils.utils import read_story, save_file, read_results
from src.generator.story_2_persona import get_persona, extract_cast
from src.generator.story_2_frag import get_fragments
from src.generator.frag_2_play import get_plays
from src.generator.play_2_image import get_play_image

# Initialize logging
setup_logging()

# Obtain a logger for this module
logger = logging.getLogger(__name__)


async def main():
    output_file = "data/output/results.json"
    results = {}

    # Uncomment and run these steps as needed
    # # 1. import story contents
    # story_content = await read_story("data/processed/ch1-4.txt")
    # save_file(story_content, "story_content", output_file)
    # logger.info("Story content saved.")
    # print(story_content)

    # # 2. generate personas
    # personas = await get_persona(story_content)
    # cast = extract_cast(personas)
    # save_file(personas, "personas", output_file)
    # save_file(cast, "cast", output_file)
    # logger.info("Personas and cast saved.")
    # print(cast)
    # print(personas)

    # # 3. generate fragments
    # fragments = await get_fragments(story_content)
    # save_file(fragments, "fragments", output_file)
    # logger.info("Fragments saved.")
    # print(fragments)

    # # 4. generate plays
    # fragments = str(read_results("fragments", output_file)).replace("\n", "")
    # cast = read_results("cast", output_file)
    #
    # plays = await get_plays(fragments, cast)
    # save_file(plays, "plays", output_file)
    # logger.info("Plays saved.")
    # print(plays)

    # # 5. generate images
    personas = read_results("personas", output_file)
    plays = read_results("plays", output_file)
    ratio = "16:9"
    style = "国风动漫"
    image_urls = []

    # Process only the first 5 plays
    for play in plays[:5]:
        image_url = get_play_image(personas, style, play, ratio)
        image_urls.append(image_url)
        logger.info(f"Generated Image URL for Play ID {play.get('id')}: {image_url}")

    save_file(image_urls, 'image_urls', output_file)
    logger.info("Image URLs saved.")


if __name__ == "__main__":
    asyncio.run(main())
