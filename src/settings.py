import os


PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')
REQUESTS_DIR = os.path.join(CONFIG_DIR, 'requests')
SERVERS_DIR = os.path.join(CONFIG_DIR, 'servers')

CSS_STATICS_DIR = os.path.join(PROJECT_DIR, 'server', 'css')
HTML_STATICS_DIR = os.path.join(PROJECT_DIR, 'server', 'html')
JS_STATICS_DIR = os.path.join(PROJECT_DIR, 'server', 'js')
