import json
import os

import tornado.web

import engine
import settings


class RequestMixin(object):
    @staticmethod
    def format_request(fname):
        requests = list(engine.read_requests(fname))

        for request in requests:
            request['template_raw'] = request['template']
            try:
                request['template'] = json.loads(request['template'])
            except ValueError as e:
                request['template'] = {'ERROR': str(e)}

        return {
            'name': fname,
            'requests': requests,
        }


class RequestsHandler(RequestMixin, tornado.web.RequestHandler):
    def get(self):
        """
        Return a list of all requests configs.
        :return:
        """
        files = os.listdir(settings.REQUESTS_DIR)

        ret = []

        for fname in sorted(files):
            f = os.path.join(settings.REQUESTS_DIR, fname)

            if os.path.isfile(f):
                ret.append(self.format_request(fname))

        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps(ret))


class RequestHandler(RequestMixin, tornado.web.RequestHandler):
    def get(self, request_name):
        """
        Return a list of all requests configs.
        :return:
        """
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps(self.format_request(request_name)))
