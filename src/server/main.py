import os

import tornado.web

import settings


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        """
        Return main page with all JS magic.
        :return:
        """

        contents = ''

        template = os.path.join(settings.HTML_STATICS_DIR, 'index.html')

        with open(template) as f:
            contents = f.read()

        self.set_header('Content-Type', 'text/html')
        self.finish(contents)
