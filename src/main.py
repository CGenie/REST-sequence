#!/usr/bin/env python

import copy
import jinja2
import json
import requests

#from reader import read_requests

def read_context():
    f = open('global-config.json')

    cfg = json.loads(f.read())

    for k, v in cfg.items():
        if k == 'global':
            continue

        for gk, gv in cfg.get('global', {}).items():
            if gk not in v:
                v[gk] = gv

    return cfg


def read_requests():
    f = open('requests.json')

    lst = []
    context = None
    for line in f:
        if line == '----\n':
            yield {
                'context': context,
                'template': '\n'.join(lst),
            }
            lst = []
        elif line.startswith('CONTEXT: '):
            context = line.replace('CONTEXT: ', '').strip()
        else:
            lst.append(line)

    if lst:
        yield {
            'context': context,
            'template': '\n'.join(lst),
        }


def perform_requests(rqs, context={}):
    for r in rqs:
        if r['context'] is not None:
            ctx = copy.deepcopy(context[r['context']])
            ctx.update(context)
        else:
            ctx = context

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
            print ('[%s] %s\nBODY: %s' % (method.upper(), url, body))
            resp = m(url, data=json.dumps(body), headers=headers)
        else:
            print ('[%s] %s' % (method.upper(), url))
            resp = m(url, headers=headers)

        print ('RESPONSE: %s' % resp.text)
        if resp.status_code < 300:
            if name in context:
                print ('WARNING: key %s already present in context, '
                       'overwriting' % name)
            context[name] = resp.json()
        else:
            print ('ERROR: http code is %d' % resp.status_code) 


if __name__ == '__main__':
    ctx = read_context()
    rqs = read_requests()
    perform_requests(rqs, context=ctx)
