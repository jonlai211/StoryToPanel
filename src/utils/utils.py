import aiofiles
import json
import os


async def read_story(filename):
    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        content = await file.read()
        return content


def save_file(data, key, filename):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                existing_data = json.load(f)
                if not isinstance(existing_data, dict):
                    existing_data = {}
            except json.JSONDecodeError:
                existing_data = {}
    else:
        existing_data = {}

    existing_data[key] = data

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=4)


def read_results(key, filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return data.get(key, None)
            except json.JSONDecodeError:
                print("Error decoding JSON from file:", filename)
                return None
    else:
        print("File does not exist:", filename)
        return None
