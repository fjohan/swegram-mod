#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from django.shortcuts import render, HttpResponse

from django.contrib.auth.models import User

def start_swedish(request):
    return render(request, 'swegram_main/start_sv.html')

def start_english(request):
    return render(request, 'swegram_main_english/start_en.html')

def swegram_main_swedish(request):
    request.session['language'] = 'sv'
    if request.session.get('file_list') and request.session.get('text_list'):
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list'] if file.activated], [])

    context = {}
    if settings.PRODUCTION:
        context['url'] = '/swegram_dev'

    return render(request, "swegram_main/main.html", context)

def swegram_main_english(request):
    request.session['language'] = 'en'
    if request.session.get('file_list') and request.session.get('text_list'):
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list'] if file.activated], [])

    context = {}
    if settings.PRODUCTION:
        context['url'] = '/swegram_dev'

    return render(request, "swegram_main_english/main.html", context)

def show_session(request):

    print('caches:')
    from django.core.cache.backends import locmem
    print(locmem._caches)

    if request.session.get('test'):
        print('TEST working')

    print('current session:')
    request.session['test'] = 1
    print(request.session.session_key)
    for r in request.session.iteritems():
        print(r)

    return HttpResponse('aa')

def u(request):
    return HttpResponse([u.username for u in User.objects.all()])
