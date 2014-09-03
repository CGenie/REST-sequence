import tornado.ioloop
import tornado.web


from . import requests
from . import servers
from . import main

import settings


def serve(port=None):
    """
    Main loop of the server
    :return:
    """

    if port is None:
        port = 8888

    print('Listening on port %d...' % port)

    application = tornado.web.Application([
        (
            r"/",
            main.MainHandler
        ),
        (
            r"/requests/?",
            requests.RequestsHandler
        ),
        (
            r"/requests/(\w+)/?",
            requests.RequestHandler
        ),
        (
            r"/servers/?",
            servers.ServersHandler
        ),
        (
            r'/static/js/(.*)',
            tornado.web.StaticFileHandler,
            {'path': settings.JS_STATICS_DIR}
        ),
        (
            r'/static/css/(.*)',
            tornado.web.StaticFileHandler,
            {'path': settings.CSS_STATICS_DIR}
        ),
    ], autoreload=True)

    application.listen(port)
    tornado.ioloop.IOLoop.instance().start()
