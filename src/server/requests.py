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
    def delete(self, request_name):
        """
        Delete request.

        :param request_name:
        :return:
        """

        self.set_header('Content-Type', 'application/json')

        if not request_name.endswith('.json'):
            request_name = '%s.json' % request_name

        os.remove(os.path.join(settings.REQUESTS_DIR, request_name))

        self.finish()

    def get(self, request_name):
        """
        Return request's config.

        :return:
        """

        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps(self.format_request(request_name)))

    def post(self, request_name):
        """
        Create/update request.

        :param request_name:
        :return:
        """

        j = json.loads(self.request.body.decode('utf-8'))

        self.set_header('Content-Type', 'application/json')
        engine.save_request(request_name, j['requests'])
        self.finish(j)


class MakeRequestHandler(RequestMixin, tornado.web.RequestHandler):
    def get(self, request_name, server_name):
        """
        Make request to server.

        :return:
        """
        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps(engine.make_request(request_name, server_name)))

