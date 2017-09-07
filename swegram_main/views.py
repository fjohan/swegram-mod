#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from django.shortcuts import render, HttpResponse

def swegram_main(request):
    if request.session.get('file_list') and request.session.get('text_list'):
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list'] if file.activated], [])

    context = {}
    if settings.PRODUCTION:
        context['url'] = '/swegram_dev'

    return render(request, "swegram_main/main.html", context)

def show_session(request):
    from django.db import connections
    from django.db.utils import OperationalError
    db_conn = connections['default']
    try:
        c = db_conn.cursor()
    except OperationalError:
        return HttpResponse('not connected')
    else:
        return HttpResponse('connected')
    print('caches:')
    from django.core.cache.backends import locmem
    print(locmem._caches)

    print('current session:')
    for r in request.session.iteritems():
        print(r)

    return HttpResponse('aa')
