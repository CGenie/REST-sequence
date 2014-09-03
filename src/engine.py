import datetime
import jinja2
import json
import requests
import os
import time

import settings


def format_datetime_now():
    return datetime.datetime.now().isoformat()


def read_context(config=None):
    f = open(os.path.join(settings.SERVERS_DIR, 'global-config.json'))

    cfg = json.loads(f.read())

    if config is not None:
        if not config.endswith('.json'):
            config = '%s.json' % config
        f = open(os.path.join(settings.SERVERS_DIR, config))
        r = f.read()
        try:
            cfg.update(json.loads(r))
        except ValueError:
            print ('Error decoding %s' % r)

    cfg['_timestamp'] = format_datetime_now()

    return cfg


def read_requests(request=None):
    if not request.endswith('.json'):
        request = '%s.json' % request

    f = open(os.path.join(settings.REQUESTS_DIR, request))

    lst = []
    dependencies = []

    for line in f:
        ln = line.rstrip('\n')

        if ln == '----':
            yield {
                'dependencies': dependencies,
                'template': '\n'.join(lst),
            }
            lst = []
            dependencies = []
        elif line.startswith('DEPENDENCIES: '):
            dependencies = line.replace('DEPENDENCIES: ', '').strip().split(' ')
        else:
            lst.append(ln)

    if lst:
        yield {
            'dependencies': dependencies,
            'template': '\n'.join(lst),
        }


def perform_requests(rqs, ctx={}):
    ret = []

    for r in rqs:
        push = {}

        dependencies = r.get('dependencies', [])

        for dependency in dependencies:
            rqs_ = read_requests(request=dependency)
            perform_requests(rqs_, ctx=ctx)

        t = jinja2.Template(r['template'])

        rnd = t.render(ctx)
        dd = json.loads(rnd)

        name = dd['name']
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
    return perform_requests(rqs, ctx=ctx)
