import aiohttp
import pytest


@pytest.mark.asyncio
async def test_httpproxy_get():
    url = 'http://httpbin.org/status/204'
    proxy = 'http://0.0.0.0:5555'
    async with aiohttp.ClientSession() as sess:
        async with sess.get(url, proxy=proxy) as request:
            status = request.status
            assert status == 204

