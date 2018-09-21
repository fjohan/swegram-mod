#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.conf import settings

from django.shortcuts import render, HttpResponse

from django.contrib.auth.models import User

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

from handle_texts.statistics import get_pos_stats, get_freq_list,\
get_general_stats, get_length, get_readability, set_freq_limit

from handle_texts.statistics_en import get_pos_stats as get_pos_stats_en
from handle_texts.statistics_en import get_freq_list as get_freq_list_en
from handle_texts.statistics_en import get_general_stats as get_general_stats_en
from handle_texts.statistics_en import get_length as get_length_en
from handle_texts.statistics_en import get_readability as get_readability_en
from handle_texts.statistics_en import set_freq_limit as set_freq_limit_en

def get_pos_stats_v(request):
    if request.session['language'] == 'en':
        return get_pos_stats_en(request)
    else:
        return get_pos_stats(request)

def get_freq_list_v(request):
    if request.session['language'] == 'en':
        return get_freq_list_en(request)
    else:
        return get_freq_list(request)

def get_general_stats_v(request):
    if request.session['language'] == 'en':
        return get_general_stats_en(request)
    else:
        return get_general_stats(request)

def get_length_v(request):
    if request.session['language'] == 'en':
        return get_length_en(request)
    else:
        return get_length(request)

def get_readability_v(request):
    if request.session['language'] == 'en':
        return get_readability_en(request)
    else:
        return get_readability(request)

def set_freq_limit_v(request):
    if request.session['language'] == 'en':
        return set_freq_limit_en(request)
    else:
        return set_freq_limit(request)
