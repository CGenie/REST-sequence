import os


# Separator for multiple requests in the same file
REQUEST_SEPARATOR = '----'
DEPENDENCIES_MARKER = 'DEPENDENCIES: '
DEPENDENCIES_SEPARATOR = ' '


PROJECT_DIR = os.path.dirname(os.path.realpath(__file__))

CONFIG_DIR = os.path.join(PROJECT_DIR, 'config')
REQUESTS_DIR = os.path.join(CONFIG_DIR, 'requests')
SERVERS_DIR = os.path.join(CONFIG_DIR, 'servers')

if not os.path.exists(REQUESTS_DIR):
    os.makedirs(REQUESTS_DIR)

if not os.path.exists(SERVERS_DIR):
    os.makedirs(SERVERS_DIR)

CSS_STATICS_DIR = os.path.join(PROJECT_DIR, 'server', 'css')
HTML_STATICS_DIR = os.path.join(PROJECT_DIR, 'server', 'html')
JS_STATICS_DIR = os.path.join(PROJECT_DIR, 'server', 'js')
FONTS_STATICS_DIR = os.path.join(PROJECT_DIR, 'server', 'fonts')
