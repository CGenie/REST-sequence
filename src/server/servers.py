import json
import os
import tornado.web

import engine
import settings


class ServerMixin(object):
    @staticmethod
    def format_server(fname):
        with open(os.path.join(settings.SERVERS_DIR, fname)) as f:
            content = f.read()

        try:
            content_json = json.loads(content)
        except ValueError as e:
            content_json = {'ERROR': str(e)}

        return {
            'name': fname,
            'config_raw': content,
            'config': content_json,
        }



class ServersHandler(ServerMixin, tornado.web.RequestHandler):
    def get(self):
        """
        Return a list of all servers configs.
        :return:
        """
        files = os.listdir(settings.SERVERS_DIR)

        ret = []

        for fname in sorted(files):
            f = os.path.join(settings.SERVERS_DIR, fname)

            if os.path.isfile(f):
                ret.append(self.format_server(fname))

        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps(ret))


class ServerHandler(ServerMixin, tornado.web.RequestHandler):
    def delete(self, server_name):
        """
        Delete server.

        :param server_name:
        :return:
        """

        self.set_header('Content-Type', 'application/json')

        if not server_name.endswith('.json'):
            server_name = '%s.json' % server_name

        os.remove(os.path.join(settings.SERVERS_DIR, server_name))

        self.finish()

    def get(self, server_name):
        """
        Return server's config.

        :return:
        """

        self.set_header('Content-Type', 'application/json')
        self.finish(json.dumps(self.format_server(server_name)))

    def post(self, server_name):
        """
        Create/update server.

        :param server_name:
        :return:
        """

        j = json.loads(self.request.body.decode('utf-8'))

        self.set_header('Content-Type', 'application/json')
        engine.save_server(server_name, j['config'])
        self.finish(j)
