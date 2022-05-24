import asyncio
import json
import os
import re
import urllib
import uuid

from lxml.html.clean import Cleaner

from config import docker_gateway
from exceptions import MethodIsNotImplemented


class StrHelpers:

    @staticmethod
    def clean_html(htl_data: str):
        cleaner = Cleaner()
        cleaner.javascript = True
        cleaner.style = True

        return cleaner.clean_html(htl_data)

    @staticmethod
    def str_to_bool(str_value, default_value=False):
        if not str_value:
            return default_value

        elif isinstance(str_value, bool):
            return str_value

        elif str_value.lower() in ('yes', 'true', 't', 'y', '1'):
            return True

        elif str_value.lower() in ('no', 'false', 'f', 'n', '0'):
            return False

    @staticmethod
    def normalize_dict_values(dict_object):
        for _arg, _value in dict_object.items():
            if not isinstance(_value, str):
                continue
            try:
                _new_val = urllib.parse.unquote(_value)
                dict_object[_arg] = _new_val
            except Exception:
                pass

        return dict_object

    @staticmethod
    def params_to_dict(params):
        proxy_param = params.get('proxy', None)
        proxy_param = proxy_param.replace('127.0.0.1', docker_gateway) \
            if proxy_param and '127.0.0.1' in proxy_param else None

        new_task_object = {
            'id': str(uuid.uuid4()),
            'method': 'get_page_content_after_click_sequence',
            'url': params.query.get('url'),
            'click_xpath_list': json.loads(
                urllib.parse.unquote(params.get('click_xpath_list'))
            ),
            'modals_xpath_list': json.loads(urllib.parse.unquote(
                params.get('modals_xpath_list'))
            ) if params.get('modals_xpath_list') else None,
            'wait_time': int(params.get('wait_time', 0)) or None,
            'use_cache': StrHelpers.str_to_bool(
                params.get('use_cache', False)
            ),
            'save_cache': StrHelpers.str_to_bool(
                params.get('save_cache', False)
            ),
            'proxy': proxy_param,
            'use_stealth': StrHelpers.str_to_bool(
                params.get('use_stealth', True)
            ),
            'is_headless': StrHelpers.str_to_bool(
                params.get('is_headless', True)
            )
        }
        return StrHelpers.normalize_dict_values(new_task_object)


class UrlParseHelper:

    @staticmethod
    def parse_domain_name(url):
        root_url = re.search(r'.*?http[s]?://([^/]*).*?', url)

        if root_url:
            return root_url.group(1)


class FsHelper:

    @classmethod
    def make_fs_file_path(cls, path, file_name=None, ext=None):
        if not file_name:
            file_name = f'{uuid.uuid4()}'
        if ext:
            ext = f'.{ext}'

        file_name = f'{file_name}{ext}'

        os.makedirs(path, exist_ok=True)
        fs_path = os.path.join(path, file_name)

        return fs_path, file_name


class GeneratorHelper:

    @classmethod
    def generate_seq_iter(cls):
        idx = 0
        while True:
            yield idx
            idx += 1


class DecoratorHelper:

    @staticmethod
    def async_loop(f):
        def decorated(obj, *args, **kwargs):
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(f(obj, *args, **kwargs))

        return decorated

    @staticmethod
    def auto_page_screenshot(f):
        def decorated(obj, *args, **kwargs):
            page_screenshot_method = getattr(obj, 'get_page_screenshot', None)
            use_auto_screenshot = getattr(obj, 'use_auto_screenshot', False)

            result = f(obj, *args, **kwargs)
            if not page_screenshot_method:
                raise MethodIsNotImplemented('get_page_screenshot')
            if use_auto_screenshot:
                page_screenshot_method()

            return result

        return decorated

    @staticmethod
    def auto_page_screenshot_async(f):
        async def decorated(obj, *args, **kwargs):
            page_screenshot_method = getattr(obj, 'get_page_screenshot', None)
            use_auto_screenshot = getattr(obj, 'use_auto_screenshot', False)

            result = await f(obj, *args, **kwargs)
            if not page_screenshot_method:
                raise MethodIsNotImplemented('get_page_screenshot')
            if use_auto_screenshot:
                await page_screenshot_method()

            return result

        return
