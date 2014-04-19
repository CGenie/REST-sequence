#!/usr/bin/env python

import copy
import datetime
import jinja2
import json
import requests
import os
import sys

#from reader import read_requests

def format_datetime_now():
    return datetime.datetime.now().isoformat()


def read_context(config=None):
    f = open(os.path.join('config', 'global-config.json'))

    cfg = json.loads(f.read())

    if config is not None:
        if not config.endswith('.json'):
            config = '%s.json' % config
        f = open(os.path.join('config', config))
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

    f = open(os.path.join('config', request))

    lst = []
    dependencies = []

    for line in f:
        if line == '----\n':
            yield {
                'dependencies': dependencies,
                'template': '\n'.join(lst),
            }
            lst = []
            dependencies = []
        elif line.startswith('DEPENDENCIES: '):
            dependencies = line.replace('DEPENDENCIES: ', '').strip().split(' ')
        else:
            lst.append(line)

    if lst:
        yield {
            'dependencies': dependencies,
            'template': '\n'.join(lst),
        }


def perform_requests(rqs, ctx={}):
    for r in rqs:
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
        if method in ['post', 'put']:
            print ('%s: %s\nBODY: %s' % (method.upper(), url, body))
            resp = m(url, data=json.dumps(body), headers=headers)
        else:
            print ('%s: %s' % (method.upper(), url))
            resp = m(url, headers=headers, verify=False)

        print ('RESPONSE: %s' % resp.text)
        if resp.status_code < 300:
            if name in ctx:
                print ('WARNING: key %s already present in context, '
                       'overwriting' % name)
            try:
                ctx[name] = resp.json()
            except ValueError:
                print ('WARNING: error decoding JSON in body')
                ctx[name] = {}
            if isinstance(ctx[name], dict):
                ctx[name]['_timestamp'] = format_datetime_now()
        else:
            print ('ERROR: http code is %d' % resp.status_code) 


if __name__ == '__main__':
    request = None
    config = None

    if len(sys.argv) == 1:
        print ('Usage: %s <request> [<context>]' % sys.argv[0])
        sys.exit(1)

    request = sys.argv[1]

    if len(sys.argv) >= 3:
        config = sys.argv[2]

    ctx = read_context(config=config)
    rqs = read_requests(request=request)
    perform_requests(rqs, ctx=ctx)
