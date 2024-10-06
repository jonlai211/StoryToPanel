import asyncio
import logging
import os
import argparse
import sys

# Adjust sys.path to include the parent directory if running from StoryToPanel
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from src.utils.logger import setup_logging  # Ensure this path is correct
from src.utils.utils import read_story, save_file, read_results
from src.generator.story_2_persona import get_persona, extract_cast
from src.generator.story_2_frag import get_fragments
from src.generator.frag_2_play import get_plays
from src.generator.play_2_image import get_play_image

# Initialize logging
setup_logging()

# Obtain a logger for this module
logger = logging.getLogger(__name__)


async def import_story(story_file: str, output_file: str):
    """
    Imports story content from a text file and saves it to the output JSON file.
    """
    logger.info(f"Importing story from {story_file}")
    story_content = await read_story(story_file)
    save_file(story_content, "story_content", output_file)
    logger.info("Story content saved.")
    print("Story content imported successfully.")


async def generate_personas(output_file: str):
    """
    Generates personas from the story content and saves them to the output JSON file.
    """
    logger.info("Generating personas")
    story_content = read_results("story_content", output_file)
    personas = await get_persona(story_content)
    cast = extract_cast(personas)
    save_file(personas, "personas", output_file)
    save_file(cast, "cast", output_file)
    logger.info("Personas and cast saved.")
    print("Personas generated successfully.")


async def generate_fragments(output_file: str):
    """
    Generates fragments from the story content and saves them to the output JSON file.
    """
    logger.info("Generating fragments")
    story_content = read_results("story_content", output_file)
    fragments = await get_fragments(story_content)
    save_file(fragments, "fragments", output_file)
    logger.info("Fragments saved.")
    print("Fragments generated successfully.")


async def generate_plays(output_file: str):
    """
    Generates plays from fragments and cast, then saves them to the output JSON file.
    """
    logger.info("Generating plays")
    fragments_list = read_results("fragments", output_file)

    # Ensure fragments_list is a list
    if not isinstance(fragments_list, list):
        logger.error(f"Expected 'fragments' to be a list, but got {type(fragments_list)}")
        print(f"Error: Expected 'fragments' to be a list, but got {type(fragments_list)}")
        return

    # Concatenate all fragments into a single string
    fragments = ''.join(fragments_list).replace("\n", "")

    cast = read_results("cast", output_file)
    print("Cast:", cast)
    plays = await get_plays(fragments, cast)
    save_file(plays, "plays", output_file)
    logger.info("Plays saved.")
    print("Plays generated successfully.")


def generate_images(output_file: str, style: str, ratio: str, limit: int = None):
    """
    Generates images from personas and plays, then saves the image URLs to the output JSON file.
    """
    logger.info("Generating images")
    personas = read_results("personas", output_file)
    plays = read_results("plays", output_file)
    image_urls = []

    # Apply limit if specified
    plays_to_process = plays[:limit] if limit else plays

    for play in plays_to_process:
        image_url = get_play_image(personas, style, play, ratio)
        image_urls.append(image_url)
        logger.info(f"Generated Image URL for Play ID {play.get('id')}: {image_url}")
        print(f"Generated Image URL for Play ID {play.get('id')}: {image_url}")

    save_file(image_urls, 'image_urls', output_file)
    logger.info("Image URLs saved.")
    print("Image generation completed successfully.")


async def main(args):
    """
    Main function to execute selected steps based on command-line arguments.
    """
    output_file = args.output_file or "src/data/output/test.json"

    tasks = []

    if args.import_story:
        tasks.append(import_story(args.story_file, output_file))

    if args.generate_personas:
        tasks.append(generate_personas(output_file))

    if args.generate_fragments:
        tasks.append(generate_fragments(output_file))

    if args.generate_plays:
        tasks.append(generate_plays(output_file))

    if args.generate_images:
        # Run image generation synchronously as it's not async
        generate_images(
            output_file=output_file,
            style=args.style,
            ratio=args.ratio,
            limit=args.limit
        )

    if tasks:
        await asyncio.gather(*tasks)
    else:
        print("No steps selected. Use --help to see available options.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="StoryToPanel: Generate images from story fragments."
    )

    parser.add_argument(
        '--import_story',
        action='store_true',
        help='Import story content from a text file.'
    )
    parser.add_argument(
        '--story_file',
        type=str,
        default='src/data/processed/ch1-4.txt',
        help='Path to the story text file.'
    )
    parser.add_argument(
        '--generate_personas',
        action='store_true',
        help='Generate personas from story content.'
    )
    parser.add_argument(
        '--generate_fragments',
        action='store_true',
        help='Generate fragments from story content.'
    )
    parser.add_argument(
        '--generate_plays',
        action='store_true',
        help='Generate plays from fragments and cast.'
    )
    parser.add_argument(
        '--generate_images',
        action='store_true',
        help='Generate images from personas and plays.'
    )
    parser.add_argument(
        '--style',
        type=str,
        default='国风动漫',
        help='Style to use for image generation.'
    )
    parser.add_argument(
        '--ratio',
        type=str,
        default='16:9',
        help='Aspect ratio for image generation.'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=None,
        help='Limit the number of plays to process for image generation.'
    )
    parser.add_argument(
        '--output_file',
        type=str,
        default='src/data/output/test.json',
        help='Path to the output JSON file.'
    )

    # Parse arguments
    args = parser.parse_args()

    # Run the main function
    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting...")
        sys.exit(0)
