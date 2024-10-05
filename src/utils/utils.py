import aiofiles


async def read_file(filename):
    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        content = await file.read()
        return content
