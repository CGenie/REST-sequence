import json
import os
import tornado.web

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
