import asyncio
import base64

import aiohttp

API_URL = "https://discord-banner-maker-api.vercel.app/make"
PASSWORD = "KAT iS STpurd"


def encode(text):
    return base64.b64encode(text.encode()).decode()


async def banner_maker(pfp_url, text1, text2, bg=None):
    params = {
        "pass": encode(PASSWORD),
        "pfp": encode(pfp_url),
        "text1": encode(text1),
        "text2": encode(text2),
    }
    if bg:
        params["bg"] = encode(bg)

    async with aiohttp.ClientSession() as session:
        async with session.get(API_URL, params=params) as response:
            if response.status == 200:
                return await response.text()
            else:
                return None
