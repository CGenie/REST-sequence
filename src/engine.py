import datetime
import jinja2
import json
import requests
import os
import time
import traceback

import settings


class MakeRequestException(Exception):
    def __init__(self, message, request=None, template=None):
        super(MakeRequestException, self).__init__(message)

        self.message = message
        self.request = request
        self.template = template


def json_name(name):
    if name.endswith('.json'):
        return name

    return '%s.json' % name


def no_json_name(name):
    return name.replace('.json', '')


def server_path(name):
    return os.path.join(settings.SERVERS_DIR, json_name(name))


def request_path(name):
    return os.path.join(settings.REQUESTS_DIR, json_name(name))


def format_datetime_now():
    return datetime.datetime.now().isoformat()


def read_context(config=None):
    f = open(server_path('global-config'))

    cfg = json.loads(f.read())

    if config is not None:
        f = open(server_path(config))
        r = f.read()
        try:
            cfg.update(json.loads(r))
        except ValueError:
            print ('Error decoding %s' % r)

    cfg['_timestamp'] = format_datetime_now()

    return cfg


def read_requests(request=None):
    f = open(request_path(request))

    lst = []
    dependencies = []

    for line in f:
        ln = line.rstrip('\n')

        if ln == settings.REQUEST_SEPARATOR:
            yield {
                'name': request,
                'dependencies': dependencies,
                'template': '\n'.join(lst),
            }
            lst = []
            dependencies = []
        elif line.startswith(settings.DEPENDENCIES_MARKER):
            dependencies = line.replace(
                settings.DEPENDENCIES_MARKER, ''
            ).strip().split(settings.DEPENDENCIES_SEPARATOR)
        else:
            lst.append(ln)

    if lst:
        yield {
            'name': request,
            'dependencies': dependencies,
            'template': '\n'.join(lst),
        }


def save_request(name, contents):
    """
    :param name: Can end in .json or not
    :param contents: List of requests as returned by read_requests.
    :return:
    """
    ret = []
    for request in contents:
        req = []
        if request['dependencies']:
            req.append('%s %s' % (
                    settings.DEPENDENCIES_MARKER,
                    settings.DEPENDENCIES_SEPARATOR.join(request['dependencies'])
                )
            )
        req.append(json.dumps(request['template'], indent=4, sort_keys=True))

        ret.append('\n'.join(req))

    with open(request_path(name), 'w') as f:
        f.write(settings.REQUEST_SEPARATOR.join(ret))


def save_server(name, config):
    """
    :param name: Can end in .json or not
    :param contents: Dict with server's config.
    :return:
    """

    with open(server_path(name), 'w') as f:
        f.write(json.dumps(config, indent=4, sort_keys=True))


def perform_requests(rqs, ctx={}):
    ret = []

    for r in rqs:
        push = {}

        name = r['name']

        dependencies = r.get('dependencies', [])

        for dependency in dependencies:
            rqs_ = read_requests(request=dependency)
            perform_requests(rqs_, ctx=ctx)

        t = jinja2.Template(r['template'])

        try:
            rnd = t.render(ctx)
        except jinja2.TemplateError as e:
            raise MakeRequestException(
                e.message,
                request=name,
                template=r['template']
            )

        dd = json.loads(rnd)

        url = dd['url']
        method = dd['method'].lower()
        body = dd.get('body')
        headers = dd.get('headers', {})

        m = getattr(requests, method)
        start = time.clock()

        push['method'] = method.upper()
        push['url'] = url

        if method in ['post', 'put']:
            push['body'] = body
            print('%s: %s\nBODY: %s' % (method.upper(), url, body))
            resp = m(url, data=json.dumps(body), headers=headers)
        else:
            print('%s: %s' % (method.upper(), url))
            resp = m(url, headers=headers, verify=False)
        end = time.clock()

        try:
            resp_text = json.dumps(resp.json(), indent=2, sort_keys=True)
            resp_json = resp.json()
        except ValueError:
            resp_text = resp.text
            resp_json = resp.text

        push['time'] = end - start
        push['response'] = resp_json
        push['status'] = resp.status_code

        print('TIME: %s' % (end - start))
        print('RESPONSE: %s' % resp_text)
        if resp.status_code < 300:
            if name in ctx:
                print('WARNING: key %s already present in context, '
                       'overwriting' % name)
            try:
                ctx[name] = resp.json()
            except ValueError:
                print('WARNING: error decoding JSON in body')
                ctx[name] = {}
            if isinstance(ctx[name], dict):
                ctx[name]['_timestamp'] = format_datetime_now()
        else:
            print('ERROR: http code is %d' % resp.status_code)

        ret.append(push)

    return ret


def make_request(request, config):
    ctx = {
        'datetime': datetime,
    }

    ctx.update(read_context(config=config))
    rqs = read_requests(request=request)

    try:
        ret = perform_requests(rqs, ctx=ctx)

        return {
            'responses': ret,
        }
    except MakeRequestException as e:
        return {
            'error': e.message,
            'details': traceback.format_exc(),
            'request': e.request,
            'template': e.template,
        }
