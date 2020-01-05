import aiohttp

async def get_page(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

async def get_file_size(url: str) -> int:
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            size = response.headers.get('Content-Length')
    if size: return int(size)

async def get_file_type(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            return response.headers.get('Content-Type')