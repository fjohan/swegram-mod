#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from django.shortcuts import render, HttpResponse

def swegram_main(request):
    if request.session.get('file_list') and request.session.get('text_list'):
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list'] if file.activated], [])

    context = {}
    if not settings.PRODUCTION: # If in production
        context['url'] = '/swegram_dev'

    return render(request, "swegram_main/main.html", context)

def show_session(request):
    print('caches:')
    from django.core.cache.backends import locmem
    print(locmem._caches)

    print('current session:')
    for r in request.session.iteritems():
        print(r)

    return HttpResponse('aa')
