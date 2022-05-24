import base64
import os

BROWSER_SERVICE_DIR = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))

redis_conf = {
    'host': os.environ.get('REDIS_HOST', '127.0.0.1'),
    'port': os.environ.get('REDIS_PORT', 6379),
}
rabbitmq_config = {
        'host': os.environ.get('RABBITMQ_HOST', '127.0.0.1'),
        'port': os.environ.get('RABBITMQ_PORT', 5672),
        'login': 'browserlib',
        'password': 'browserlib123',
        'virtualhost': 'browser_parsing'
    }

custom_redis_logger_key = 'browser_lib_logger'
pyppeteer_bin = None
docker_gateway = os.environ.get('DOCKER_GATEWAY')

app_port = os.environ.get('PYPPETEER_API_PORT', 8080)
app_host = os.environ.get('PYPPETEER_API_HOST', '0.0.0.0')
is_docker = os.environ.get('PYPPETEER_DOCKER', False)

proxy_broker_host = os.environ.get('PROXY_BROKER_HOST', '127.0.0.1')
proxy_broker_port = os.environ.get('PROXY_BROKER_PORT', '8000')
proxy_broker_url = f'http://{proxy_broker_host}:{proxy_broker_port}' \
    if all((proxy_broker_host, proxy_broker_host)) else None

if is_docker:
    pyppeteer_bin = '/usr/bin/google-chrome'

browser_storage_dir = os.path.join(
    BROWSER_SERVICE_DIR,
    'browserlib-service',
    'loader_task_api',
    'static',
    'browser_storage'
)

browser_bin = {
    'firefox': os.path.join(
        BROWSER_SERVICE_DIR,
        'browserlib-service',
        'browser_bin', 'geckodriver'
    ),
    'chrome': os.path.join(
        BROWSER_SERVICE_DIR,
        'browserlib-service',
        'browser_bin', 'chromedriver'),
    'pyppeteer': pyppeteer_bin
}

jinja2_templates = os.path.join(
    BROWSER_SERVICE_DIR,
    'browserlib-service',
    'pyppeteer_task_api',
    'templates'
)

path_dict = {
    'browser_storage_dir': browser_storage_dir
}
browser_storage_url = '/static/browser_storage/'

is_headless = True
use_proxy_broker = False

rabbitmq_params = {
    'host': os.environ.get('RABBITMQ_HOST', '127.0.0.1'),
    'port': os.environ.get('RABBITMQ_PORT', 5672),
    'virtual_host': 'browser_parsing',
    'credentials': {
        'username': 'browserlib',
        'password': 'browserlib123'
    }
}


number_of_workers = int(os.getenv('PYPPETEER_NUMBER_OF_WORKERS', 2))
