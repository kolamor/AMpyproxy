import asyncio
from asyncio import StreamReader, StreamWriter
from proxys import Proxy, ProxyFactory
from proxy_client import ProxyClient
import logging

logger = logging.getLogger(__file__)


class ServerReader:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self._reader = reader
        self._writer = writer
        self.write_timeout = 10
        self.read_timeout = 10
        self.start_row = b''

    @classmethod
    async def init(cls, reader: StreamReader, writer: StreamWriter) -> 'ServerReader':
        self = cls(reader=reader, writer=writer)
        self.start_row = await self.readline()
        return self

    async def send(self, data: bytes):
        self._writer.write(data)
        await asyncio.wait_for(self._writer.drain(), self.write_timeout)

    async def readline(self) -> bytes:
        line = await asyncio.wait_for(
            self._reader.readline(), self.read_timeout
        )
        return line

    async def read(self, chunk_limit: int = 2**12) -> bytes:
        reader = self._reader
        data = await asyncio.wait_for(
            reader.read(chunk_limit), self.read_timeout
        )
        return data

    def reader_at_of(self):
        return self._reader.at_eof()


class Synchronizer:
    def __init__(self, server_connect: ServerReader, client_connect: ProxyClient):
        self.server_connect = server_connect
        self.client_connect = client_connect

    @classmethod
    async def init(cls, server_connect: ServerReader) -> 'Synchronizer':
        client_connect = await cls._create_client_connect()
        self = cls(server_connect=server_connect, client_connect=client_connect)
        return self

    @classmethod
    async def _create_client_connect(cls) -> ProxyClient:
        proxy = ProxyFactory.get_proxy()
        client_connect = await ProxyClient.init(proxy=proxy)
        return client_connect

    async def start(self):
        start_row = self.server_connect.start_row
        print(start_row)
        await self.client_connect.create_proxy_connect(start_row)
        task_server = asyncio.create_task(self.away(self.server_connect, self.client_connect))
        task_client = asyncio.create_task(self.away(self.client_connect, self.server_connect))
        await asyncio.gather(task_server, task_client)
        logger.debug('disconect')

    async def away(self, reader, writer):
        try:
            while not reader.reader_at_of():
                chunk = await reader.read()
                if chunk == b'':
                    await asyncio.sleep(0)
                    break
                await writer.send(chunk)
                await asyncio.sleep(0)
        except Exception as e:
            logger.debug(f'{e, e.args}')
        finally:
            pass

async def handler(reader: StreamReader, writer: StreamWriter):
    server_connect = await ServerReader.init(reader=reader, writer=writer)
    synchronizer = await Synchronizer.init(server_connect=server_connect)
    await synchronizer.start()


async def start():
    print('start')
    try:
        srv = await asyncio.start_server(handler, host='0.0.0.0', port=5555, )
        await srv.serve_forever()
    finally:
        # await srv.wait_closed()
        await asyncio.sleep(1)
        print('stop')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    asyncio.run(start(), debug=True)
