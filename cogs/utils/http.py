import aiohttp

async def get_page(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

async def get_headers(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.head(url) as response:
            return response.headers 

async def get_file_size(url: str) -> int:
    headers = await get_headers(url)
    size = headers.get('Content-Length')
    if size: return int(size)

async def get_file_type(url: str) -> str:
    headers = await get_headers(url)
    return headers.get('Content-Type')