#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import config

upload_location = config.UPLOAD_LOCATION

from django.core.signals import request_finished

from django.http import JsonResponse, HttpResponse

from tempfile import NamedTemporaryFile
from wsgiref.util import FileWrapper
from django.utils.encoding import smart_str

import os

import statistics

def set_stats_type(request):
    text_id = None
    for prop in request.GET:
        if prop == 'id':
            text_id = request.GET[prop]

    if text_id == 'all_texts':
        if request.session['single_text']:
            del request.session['single_text']
        request.session['text_list'] = sum([[text for text in file.texts] for file in request.session['file_list']], [])
    else:
        texts = sum([file.texts for file in request.session['file_list']], [])
        request.session['single_text'] = [text for text in texts if text.id == int(text_id)]

    return JsonResponse({})

def visualise_text(request):
    t = None
    text_id = None

    for prop in request.GET:
        if prop == 'text_id':
            text_id = int(request.GET[prop])

    for text in request.session['text_list']:
        if text.id == text_id:
            t = text


    if t.metadata:
        metadata = ' '.join(t.metadata)
    else:
        metadata = config.NO_METADATA_STRING

    data = {
            'metadata': metadata,
            'sentences': [[token.__dict__ for token in sentence.tokens] for sentence in t.sentences],
            'pos_list': sorted(t.pos_counts.keys()),
            'text_id': t.id
           }


    return JsonResponse(data)

def set_filename(request):
    new_filename = None
    file_id = None

    for prop in request.GET:
        if prop == 'new_filename':
            new_filename = request.GET[prop]
        elif prop == 'file_id':
            file_id = int(request.GET[prop])

    for file in request.session.get('file_list'):
        if file.file_id == file_id:
            file.filename = new_filename

    context = statistics.basic_stats(request.session['text_list'], request)

    return JsonResponse(context)

def edit_token(request):
    text_id = None
    token_id = None
    set_type = None
    new_value = None

    for prop in request.GET:
        if prop == 'text_id':
            text_id = int(request.GET[prop])
        elif prop == 'token_id':
            token_id = int(request.GET[prop])
        elif prop == 'type':
            set_type = request.GET[prop]
        elif prop == 'new_value':
            new_value = request.GET[prop]

    if text_id == None or token_id == None or set_type == None or new_value == None:
        return JsonResponse({})

    text = None
    for t in request.session['text_list']:
        if t.id == text_id:
            for sentence in t.sentences:
                for token in sentence.tokens:
                    if token.id == token_id:
                        setattr(token, set_type, new_value.encode('UTF-8'))

    return JsonResponse({})

def update_metadata(request):
    def invert(bool):
        return not bool

    meta = None
    for prop in request.GET:
        if prop == 'meta':
            meta = request.GET['meta']

    meta_label = meta.split("_")[0]
    meta_prop = meta.split("_")[1]
    request.session['metadata'][meta_label][meta_prop][0] = invert(request.session['metadata'][meta_label][meta_prop][0])
    return JsonResponse({})

def text_eligibility(request, text):
    if not text.activated:
        return False
    if text.eligible and not text.metadata:

        return True

    metadata_dict = request.session.get('metadata')

    for x in range(len(text.metadata_labels)):
        for y in range(len(text.metadata)):
            if metadata_dict[text.metadata_labels[x]][text.metadata[x]][0] == False:
                return False
    return True


def add_text_metadata(request, file_id):
    if not request.session.get('metadata'):
        request.session['metadata'] = {}

    for file in request.session.get('file_list'):
        if file.has_metadata and file.file_id == file_id and file.activated:
            file.meta_added = True
            for text in file.texts:
                for x in range(len(text.metadata_labels)):
                    if text.metadata_labels[x] in request.session['metadata']:
                        if text.metadata[x] in request.session['metadata'][text.metadata_labels[x]]:
                            request.session['metadata'][text.metadata_labels[x]][text.metadata[x]][1] += 1
                        else:
                            request.session['metadata'][text.metadata_labels[x]][text.metadata[x]] = [True, 1]
                    else:
                        request.session['metadata'][text.metadata_labels[x]] = {text.metadata[x]: [True, 1]}
    return request

def remove_text_metadata(request, file_id):
    for file in request.session.get('file_list'):
        if file.file_id == file_id and file.meta_added:
            file.meta_added = False
            for text in file.texts:
                for x in range(len(text.metadata_labels)):
                    if text.metadata_labels[x] in request.session['metadata']:
                        if text.metadata[x] in request.session['metadata'][text.metadata_labels[x]]:
                            request.session['metadata'][text.metadata_labels[x]][text.metadata[x]][1] -= 1
                            if request.session['metadata'][text.metadata_labels[x]][text.metadata[x]][1] == 0:
                                del request.session['metadata'][text.metadata_labels[x]][text.metadata[x]]
                            if not request.session['metadata'][text.metadata_labels[x]]:
                                del request.session['metadata'][text.metadata_labels[x]]
    return request

def handle_uploaded_file(f):
    fname = str(f)
    dest = upload_location + fname
    with open(dest, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def str_to_bool(s):
    return True if s.lower() == "true" else False

# Remove any empty lines in the beginning
def rm_blanks(text_list):
    while True:
        if text_list[0] == '\n':
            del text_list[0]
        else:
            break
    return text_list

def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def checkbox_to_bool(s):
    return True if s == "on" else False

def download_file(request, file_id, get_md5=False):
    file_to_dl = [f for f in request.session['file_list']\
    if f.file_id == int(file_id)][0]

    f = NamedTemporaryFile(delete=False)

    def test_signal(sender, **kwargs):
        os.remove(f.name)
    request_finished.connect(test_signal, weak=False)
    request_finished.disconnect(test_signal)

    f.write('<' + ' '.join(file_to_dl.metadata_labels) + '>\n')

    for text in file_to_dl.texts:
        f.write('<' + ' '.join(text.metadata) + '>')
        f.write('\n')
        for sentence in text.sentences:
            for token in sentence.tokens:
                f.write(
                token.text_id + '\t' +
                token.token_id + '\t' +
                token.form + '\t' +
                token.norm + '\t' +
                token.lemma + '\t' +
                token.upos + '\t' +
                token.xpos + '\t' +
                token.feats + '\t' +
                token.ufeats + '\t' +
                token.head + '\t' +
                token.deprel + '\t' +
                token.deps + '\t' +
                token.misc
                )
            f.write('\n')

    f.close()

    import hashlib
    print('md5 downloadable', hashlib.md5(f.name).hexdigest())
    print('md5 raw contents', hashlib.md5(file_to_dl.raw_contents).hexdigest())

    response = HttpResponse(FileWrapper(open(f.name)), content_type='application/force-download')

    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(file_to_dl.filename)

    return response

def update_sidebar(request):
    if not request.session.get('file_list'):
        return JsonResponse({})
    fl = request.session['file_list']
    tl = request.session['text_list']



    for prop in request.GET:
        if prop == 'rm':
            file_to_remove = int(request.GET[prop])
            request = remove_text_metadata(request, file_to_remove)
            request.session['file_list'] = [f for f in fl if f.file_id != file_to_remove]
            request.session['text_list'] = [t for t in tl if t.file_id != file_to_remove]

        elif prop == 'set_state':
            file_to_change = int(request.GET[prop])
            request.session['file_list'] = [f.toggle_activate() if f.file_id == file_to_change else f for f in fl]
            request.session['text_list'] = [t.toggle_activate() if t.file_id == file_to_change else t for t in tl]

            for f in request.session['file_list']:
                if f.file_id == file_to_change:
                    if f.activated:
                        add_text_metadata(request, file_to_change)
                    else:
                        remove_text_metadata(request, file_to_change)

    eligible_texts = statistics.get_text_list(request)

    context = statistics.basic_stats(eligible_texts, request)


    return JsonResponse(context)
