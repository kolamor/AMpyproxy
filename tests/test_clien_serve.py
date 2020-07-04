import pytest_asyncio
import pytest
import pathlib
import base64
from .. import Client, Proxy, ProxyClient

from asyncio import StreamReader, StreamWriter
import asyncio


def get_path():
    path = pathlib.Path(__file__).parent.parent.absolute() / '.secrets/proxy'
    return path


def get_proxy():
    with open(get_path()) as f:
        proxy = f.read().split('\n')[0]
        return proxy


@pytest.mark.asyncio
async def test_client_connect():
    reader, writer = await Client._open_connection('httpbin.org', 80)
    assert isinstance(reader, StreamReader)
    assert isinstance(writer, StreamWriter)
    send_data = b"GET /status/200 HTTP/1.1\r\nHost: httpbin.org\r\n\r\n"
    writer.write(send_data)
    await writer.drain()
    read_data = await reader.readuntil(b'\r\n\r\n')
    assert b'HTTP/1.1 200 OK\r\n' in read_data


@pytest.mark.asyncio
async def test_Client_send_read():
    proxy_client = await Client.init('httpbin.org', 80)
    send_data = b"GET /status/200 HTTP/1.1\r\nHost: httpbin.org\r\n\r\n"
    await proxy_client.send(send_data)
    read_data = await proxy_client.read()
    assert b'HTTP/1.1 200 OK\r\n' in read_data


def test_Proxy():
    scheme = 'http'
    user = 'iser'
    password = 'mypassword'
    host = '192.164.11.177'
    port = '8888'
    proxy = f'{scheme}://{user}:{password}@{host}:{port}'
    instance_proxy = Proxy(proxy=proxy)
    assert instance_proxy.scheme == scheme
    assert instance_proxy.user == user
    assert instance_proxy.password == password
    assert instance_proxy.host == host
    assert instance_proxy.port == port
    credentials = base64.b64decode(instance_proxy.user_pass_base64)
    assert credentials == f'{user}:{password}'.encode()


@pytest.mark.asyncio
async def test_proxy_connect():
    proxy = Proxy(get_proxy())
    proxy_client = await ProxyClient.init(proxy)
    data = f"GET http://httpbin.org/status/202 HTTP/1.1\r\nHost: httpbin.org\r\n".encode()
    await proxy_client.create_proxy_connect(data)
    await proxy_client.send(b'\r\n')
    read_data = await proxy_client.read()
    assert b'202 Accepted' in read_data


@pytest.mark.asyncio
async def test_Client_http_get_request():
    data = b'''Host: httpbin.org\r\n
        User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0\r\n
        Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8\r\n
        Accept-Language: ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3\r\n
        Accept-Encoding: gzip, deflate\r\n
        Connection: keep-alive\r\n
        \r\n
        '''
    start_row = b'GET http://httpbin.org/status/204 HTTP/1.1\r\n'
    proxy = Proxy(get_proxy())
    proxy_client = await ProxyClient.init(proxy)
    await proxy_client.create_proxy_connect(start_row)
    await proxy_client.send(data=data)
    read_data = await proxy_client.read()
    assert b'204 No Content' in read_data










# @pytest.mark.asyncio
# async def test_proxy_client():
#     proxy = Proxy(get_proxy())
#     client = await Client.init('httpbin.org/ip', proxy, 'GET')
#     text_resp = await client.test_receive()
#     assert text_resp == proxy.host
#     print(text_resp)
#

