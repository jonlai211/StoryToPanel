import json
import os
import requests
from PIL import Image
from io import BytesIO


def download_image(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Failed to download image from {url}: {e}")
        return None


def crop_image(image, region):
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
        print(f"Invalid region number: {region}. Must be between 1 and 4.")
        return None

    return image.crop((left, top, right, bottom))


def main():
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    results_json_path = os.path.join(script_dir, '../data/output/results.json')
    output_dir = os.path.join(script_dir, '../data/images')

    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load results.json
    try:
        with open(results_json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read {results_json_path}: {e}")
        return

    image_urls = data.get('image_urls', [])
    total_images = len(image_urls)
    print(f"Total image URLs found: {total_images}")

    for idx, url in enumerate(image_urls, start=1):
        if url is None:
            print(f"Play ID {idx}: No image URL found. Skipping.")
            continue

        print(f"Play ID {idx}: Downloading image from {url}")
        image = download_image(url)
        if image is None:
            print(f"Play ID {idx}: Failed to download image. Skipping.")
            continue

        for region in range(1, 5):
            cropped = crop_image(image, region)
            if cropped is not None:
                image_filename = f"{idx}_{region}.jpg"
                image_path = os.path.join(output_dir, image_filename)
                try:
                    cropped.save(image_path)
                    print(f"Play ID {idx}: Saved cropped image as {image_filename}")
                except Exception as e:
                    print(f"Play ID {idx}: Failed to save image {image_filename}: {e}")
            else:
                print(f"Play ID {idx}: Failed to crop region {region}.")

    print("Image download and cropping completed.")


if __name__ == "__main__":
    main()
