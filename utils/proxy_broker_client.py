from abc import ABC, abstractmethod
from urllib.parse import urljoin

import httpx
import requests


class ProxyBrokerMethodAbstract(ABC):

    @staticmethod
    def set_headers() -> dict:
        return {'user-agent': 'proxy-broker-client'}

    @abstractmethod
    async def get_request(self, method_route, data):
        pass

    @abstractmethod
    def get_request_sync(self, method_route, data):
        pass


class ProxyGetRequestsMethods(ProxyBrokerMethodAbstract):

    def __init__(self, method_route, request_timeout, verify_ssl=False):
        self.method_route = method_route
        self.request_timeout = request_timeout
        self.verify_ssl = verify_ssl

    async def get_request(self, url, data):
        method_url = urljoin(url, self.method_route)
        headers: dict = self.set_headers()

        async with httpx.AsyncClient(headers=headers,
                                     timeout=self.request_timeout,
                                     verify=self.verify_ssl) as client:
            api_response = await client.get(method_url, params=data)
            api_response.raise_for_status()

            return api_response

    def get_request_sync(self, url, data):
        method_url = urljoin(url, self.method_route)
        headers: dict = self.set_headers()

        api_response = requests.get(
            method_url,
            params=data,
            headers=headers,
            timeout=self.request_timeout,
            verify=self.verify_ssl
        )
        api_response.raise_for_status()

        return api_response


class ProxyBrokerServiceClient:

    def __init__(self, root_url, request_timeout=20):
        self.root_url = root_url
        self.__get_proxy_method = ProxyGetRequestsMethods(
            method_route='/api/proxy', request_timeout=request_timeout
        )
        self.__get_proxy_success = ProxyGetRequestsMethods(
            method_route='/api/proxy/successful', request_timeout=request_timeout
        )
        self.__get_proxy_fail = ProxyGetRequestsMethods(
            method_route='/api/proxy/failed', request_timeout=request_timeout
        )

    async def get_proxy(self, data):
        try:
            response = await self.__get_proxy_method.get_request(self.root_url, data)
            response_json = response.json()
        except Exception as _err:
            print(f'Some problems with get_proxy: {_err}', flush=True)
        else:
            return response_json

    def get_proxy_sync(self, data):
        try:
            response = self.__get_proxy_method.get_request_sync(self.root_url, data)
            response_json = response.json()
        except Exception as _err:
            print(f'Some problems with get_proxy: {_err}', flush=True)
        else:
            return response_json

    async def get_proxy_success(self, data):
        try:
            response = await self.__get_proxy_success.get_request(self.root_url, data)
            response_json = response.json()
        except Exception as _err:
            print(f'Some problems with get_proxy: {_err}', flush=True)
        else:
            return response_json

    async def get_proxy_fail(self, data):
        try:
            response = await self.__get_proxy_fail.get_request(self.root_url, data)
            response_json = response.json()
        except Exception as _err:
            print(f'Some problems with get_proxy: {_err}', flush=True)
        else:
            return response_json
