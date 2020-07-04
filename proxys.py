import base64
import pathlib
try:
    from urllib2 import _parse_proxy
except ImportError:
    from urllib.request import _parse_proxy


def get_path():
    path = pathlib.Path(__file__).parent.absolute() / '.secrets/proxy'
    return path


PATH_FILE = get_path()


class ProxyFactory:
    path_file = PATH_FILE
    proxy = ''

    @classmethod
    def get_proxy(cls) -> 'Proxy':
        if not cls.proxy:
            proxy_url = cls.__get_from_file()
        else:
            proxy_url = cls.proxy
        return Proxy(proxy_url)

    @classmethod
    def __get_from_file(cls):
        with open(cls.path_file) as f:
            proxy = f.read().split('\n')[0]
            cls.proxy = proxy
        return proxy


class Proxy:
    def __init__(self, proxy: str):
        scheme, user, password, host_port = _parse_proxy(proxy)
        self.scheme = scheme
        self.user = user
        self.password = password
        host, port = host_port.split(':')
        self.host = host
        self.port = port
        self.user_pass_base64 = None
        if user and password:
            self.user_pass_base64 = base64.b64encode(f'{user}:{password}'.encode())
        else:
            self.user_pass_base64 = None
