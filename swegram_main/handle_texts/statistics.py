#!/usr/bin/env python
# -*- coding: utf-8 -*-

from helpers import f7, text_eligibility
import numpy as np
from django.http import JsonResponse

from collections import Counter

from .. import config

def invert(bool):
    return not bool

def get_text_list(request):
    if request.session.get('single_text'):
        return request.session['single_text']
    elif request.session.get('text_list'):

        return [text for text in request.session['text_list'] if text_eligibility(request, text)]
    else:
        return []

def basic_stats(text_list, request):

    data = {}

    data['text_ids']        = []
    for file in request.session['file_list']:
        for text in file.texts:
            if text.metadata:
                data['text_ids'].append([text.id, ' '.join(text.metadata)])
            else:
                data['text_ids'].append([text.id, config.NO_METADATA_STRING])
    #sum([[ for text in file.texts if text_eligibility(request, text)] for file in request.session['file_list']], [])
    data['texts_selected']  = len(text_list)
    data['text_n']          = len([text for text in request.session['text_list'] if text.eligible])
    data['loaded_files']    = [[a.filename,
                                a.file_id,
                                a.file_size,
                                len(a.texts),
                                a.date_added,
                                a.has_metadata,
                                a.eligible,
                                a.activated,
                                a.normalized] for a in request.session.get('file_list')]
    data['metadata']        = request.session.get('metadata')
    data['total_words']     = int(np.sum([text.word_count for text in text_list]))
    data['total_tokens']    = int(np.sum([text.token_count for text in text_list]))
    data['total_sentences'] = int(np.sum([text.sentence_count for text in text_list]))
    data['compounds']       = int(np.sum([text.compounds for text in text_list]))
    data['misspells']       = int(np.sum([text.misspells for text in text_list]))
    data['texts']           = []

    for text_file in request.session['file_list']:
        if text_file.activated:
            if text_file.has_metadata:
                data['texts'].append(
                    {
                        'filename': text_file.filename,
                        'texts_in_file': [{'meta': ' '.join(t.metadata), 'id': t.id}\
                        for t in text_file.texts]
                    }
                )
            else:
                data['texts'].append(
                    {
                        'filename': text_file.filename,
                        'texts_in_file': [{'meta': '(ingen metadata)', 'id': t.id}\
                        for t in text_file.texts]
                    }
                )

    return data

def nominal_quota(textlist):
    # Return simple, full
    nn       = 0
    vb       = 0

    nn_pp_pc = 0
    pn_ab_vb = 0

    individual_simple_nq = []
    individual_full_nq = []

    for t in textlist:
        text_nn = 0
        text_vb = 0

        text_nn_pp_pc = 0
        text_pn_ab_vb = 0

        for s in t.sentences:
            for token in s.tokens:
                if token.xpos in ['NN','PP','PC']:
                    text_nn_pp_pc += 1

                    if token.xpos == 'NN':
                        text_nn += 1
                elif token.xpos in ['PN', 'AB', 'VB']:
                    text_pn_ab_vb += 1
                    if token.xpos == 'VB':
                        text_vb += 1
            nn += text_nn
            vb += text_vb

            nn_pp_pc += text_nn_pp_pc
            pn_ab_vb += text_pn_ab_vb

        if text_nn == 0 or text_vb == 0:
            simple = 0
        else:
            text_simple_nq = (float(text_nn)/text_vb)

        if text_nn_pp_pc == 0 or text_pn_ab_vb == 0:
            full = 0
        else:
            text_full_nq = (float(text_nn_pp_pc) / text_pn_ab_vb)

        individual_simple_nq.append(text_simple_nq)
        individual_full_nq.append(text_full_nq)

    if nn == 0 or vb == 0:
        simple = 0
    else:
        simple = round((float(nn)/vb), 2)

    if nn_pp_pc == 0 or pn_ab_vb == 0:
        full = 0
    else:
        full = round((float(nn_pp_pc) / pn_ab_vb), 2)

    return round(simple, 2), round(full, 2), round(np.median(individual_simple_nq), 2), round(np.median(individual_full_nq), 2)

def ovix_ttr(textlist):
    # gets ovix (median), ovix (total), and ttr since they use the same data
    tokens = []
    individual_ovix_values = []
    individual_ttr_values = []
    for t in textlist:
        text_tokens = []
        for s in t.sentences:
            s_tokens = [token.norm.lower() for token in s.tokens if token.xpos not in ['MAD', 'MID', 'PAD']]
            text_tokens += s_tokens
            tokens += s_tokens


        text_n_tokens = float(len(text_tokens))
        text_n_types = float(len(set(text_tokens)))

        if text_n_types == 0 or text_n_tokens == 0:
            text_ovix = 0
            text_ttr = 0
        else:
            text_ovix = np.log(text_n_tokens) / np.log(2-(np.log(text_n_types)/np.log(text_n_tokens)))
            text_ttr = float(len(set(text_tokens))) / len(text_tokens)
        individual_ttr_values.append(text_ttr)
        individual_ovix_values.append(text_ovix)

    n_tokens = float(len(tokens))
    n_types = float(len(set(tokens)))

    if n_types == 0 or n_tokens == 0:
        return 0, 0, 0, 0
    if n_types == n_tokens:
        return 0, 0, 1, 1
    return round(np.median(individual_ovix_values), 2), round(np.log(n_tokens) / np.log(2-(np.log(n_types)/np.log(n_tokens))), 2),\
    round((float(len(set(tokens))) / len(tokens)), 2), round(np.median(individual_ttr_values), 2)

def lix(textlist):
    long_words = 0
    words = np.sum([text.word_count for text in textlist])
    sentences = np.sum([text.sentence_count for text in textlist])

    individual_lix_values = []

    for t in textlist:
        t_long_words = 0
        t_words = t.word_count
        t_sentences = t.sentence_count
        for s in t.sentences:
            lw = len([len(token.norm.lower()) for token in s.tokens if len(token.norm) > 6])
            long_words += lw
            t_long_words += lw
        individual_lix_values.append((float(t_words)/t_sentences) + ((t_long_words*100) / float(t_words)))

    return round(np.median(individual_lix_values), 2), round((float(words)/sentences) + ((long_words*100) / float(words)), 2)

def freq_list(text, type):

    total = 0.0
    freq_list = {}

    for sentence in text.sentences:

        for token in sentence.tokens:
            total += 1
            if type == 'form':
                if token.form.lower() + '_' + token.xpos in freq_list:
                    freq_list[token.form.lower() + '_' + token.xpos] += 1
                else:
                    freq_list[token.form.lower() + '_' + token.xpos] = 1
            elif type == 'norm':
                if token.norm.lower() + '_' + token.xpos in freq_list:
                    freq_list[token.norm.lower() + '_' + token.xpos] += 1
                else:
                    freq_list[token.norm.lower() + '_' + token.xpos] = 1
            elif type == 'lemma':
                if token.lemma.lower() + '_' + token.xpos in freq_list:
                    freq_list[token.lemma.lower() + '_' + token.xpos] += 1
                else:
                    freq_list[token.lemma.lower() + '_' + token.xpos] = 1

    for f in freq_list:
        freq_list[f] = [freq_list[f], round(freq_list[f] / total, 2)]

    sorted_words = sorted(freq_list.iteritems(), key=lambda x: int(x[1][0]), reverse=True)

    freq_as_list = []

    for x in range(len(sorted_words)):
        # index, token, count, share
        freq_as_list.append([x+1, sorted_words[x][0], sorted_words[x][1][0], sorted_words[x][1][1]])

    return freq_as_list

def set_freq_limit(request):

    def get_smaller(n):
        return int(n-25)
    def get_larger(n):
        return int(n+25)

    type = None

    for prop in request.GET:
        if prop == 'type':
            type = request.GET[prop]

    if type == 'increase':
        if len(request.session['freq_list']) < (request.session['freq_limit'] + 25):
            request.session['freq_limit'] = len(request.session['freq_list'])
        else:
            request.session['freq_limit'] = get_larger(request.session['freq_limit'])
        request.session['freq_limit']

    elif type == 'decrease':
        if request.session['freq_limit'] > 25:
            request.session['freq_limit'] = get_smaller(request.session['freq_limit'])

    elif type == 'all':
        request.session['freq_limit'] = len(request.session['freq_list'])*10

    elif type == 'reset':
        request.session['freq_limit'] = 25

    return JsonResponse({
                        'freq_type': request.session['freq_type'],
                        'freq_list': request.session['freq_list'][:request.session['freq_limit']],
                        'freq_pos_list': request.session['freq_pos_list'],
                        'non_normalized_files': request.session['non_normalized_files']
                        })


def get_freq_list(request):

    def perc_string(acc, dp=2):
        # Makes sure there's two decimals
        return ("{0:." + str(dp) + "f}").format(acc * 100) + "%"

    if not request.session.get('text_list'):
        return JsonResponse({})
    if not request.session.get('freq_limit'):
        request.session['freq_limit'] = 25

    total = 0.0
    frequencies = Counter({})

    pos_list = sorted(list(set([x for sublist in [text.pos_counts.keys() for text\
    in request.session['text_list']] for x in sublist])))


    # freq_type can be form, norm and lemma
    if not request.session.get('freq_type'):
        request.session['freq_type'] = 'norm'
    if not request.session.get('freq_pos_list'):
        request.session['freq_pos_list'] = [[x, True] for x in pos_list]

    for prop in request.GET:
        if prop == 'type_change':
            request.session['freq_type'] = request.GET[prop]
        if prop == 'toggle_freq_pos':
            for pos in request.session['freq_pos_list']:
                if pos[0] == request.GET[prop]:
                    pos[1] = invert(pos[1])
    disabled_pos = [p[0] for p in request.session['freq_pos_list'] if p[1] == False]

    text_list = get_text_list(request)

    if not request.session.get('non_normalized_files'):
        request.session['non_normalized_files'] = False

    if request.session['freq_type'] == 'norm':
        text_list = [t for t in text_list if t.normalized]
        request.session['non_normalized_files'] = [f.filename for f in request.session['file_list'] if not f.normalized]

    freq_type = 'freqlist_' + request.session['freq_type']

    for text in text_list:
        freq_dict = {}
        for entry in getattr(text, freq_type):
            total += entry[2]
            freq_dict[entry[1]] = entry[2]
        frequencies += Counter(freq_dict)

    frequencies = dict(frequencies)
    for f in frequencies.keys():
        if f.rsplit('_',1)[1] in disabled_pos:
            total -= frequencies[f]
            del frequencies[f]

    for f in frequencies:
        frequencies[f] = [frequencies[f], frequencies[f] / total]

    sorted_words = sorted(frequencies.iteritems(), key=lambda x: int(x[1][0]), reverse=True)

    sorted_words = [x for x in sorted_words if x[0].split('_')[1] not in disabled_pos]
    freq_as_list = []

    for x in range(len(sorted_words)):
        # index, token, count, share
        freq_as_list.append([x+1, sorted_words[x][0].split("_")[0], sorted_words[x][0].split("_")[1], sorted_words[x][1][0], perc_string(sorted_words[x][1][1])])

    request.session['freq_list'] = freq_as_list

    return JsonResponse({'freq_type': request.session['freq_type'],
                         'freq_list': request.session['freq_list'][:request.session['freq_limit']],
                         'freq_pos_list': request.session['freq_pos_list'],
                         'non_normalized_files': request.session['non_normalized_files']})

def get_pos_stats(request):
    def invert(bool):
        return not bool

    toggle = False
    for prop in request.GET:
        if prop == 'toggle':
            toggle = request.GET[prop]

    if not request.session.get('text_list'):
        return JsonResponse({})

    pos_list = sorted(list(set([x for sublist in [text.pos_counts.keys() for text\
    in request.session['text_list']] for x in sublist])))

    # Pos enabled has the values POS - enabled
    # enabled = whether the user has turned it on or off in the pos stats menu
    #del request.session['pos_enabled']

    if not request.session.get('pos_enabled'):
        request.session['pos_enabled'] = [[p, True] for p in pos_list]
    elif toggle: # Works as inteded now
        for pos in request.session['pos_enabled']:
            if pos[0] == toggle:
                pos[1] = invert(pos[1])
    else:
        available = [p[0] for p in request.session['pos_enabled']]
        for pos in pos_list:
            if pos not in available:
                request.session['pos_enabled'].append([pos, True])

    included_pos_tags = []
    for pos in request.session['pos_enabled']:
        if pos[1]:
            included_pos_tags.append(pos[0])

    text_list = get_text_list(request)

    return JsonResponse({'pos_counts': pos_stats(text_list, included_pos_tags), 'pos_list': request.session['pos_enabled']})


def calculate_lengths(texts, type, n, words_pos):
    occurrences = 0

    if type == 'morethan':
        for text in texts:
            for sentence in text.sentences:
                for token in sentence.tokens:
                    if words_pos == 'words':
                        if token.length > n:
                            occurrences += 1
                    else:
                        if token.length > n and token.xpos == words_pos:
                            occurrences += 1
    elif type == 'lessthan':
        for text in texts:
            for sentence in text.sentences:
                for token in sentence.tokens:
                    if words_pos == 'words':
                        if token.length < n:
                            occurrences += 1
                    else:
                        if token.length < n and token.xpos == words_pos:
                            occurrences += 1
    elif type == 'equal':
        for text in texts:
            for sentence in text.sentences:
                for token in sentence.tokens:
                    if words_pos == 'words':
                        if token.length == n:
                            occurrences += 1
                    else:
                        if token.length == n and token.xpos == words_pos:
                            occurrences += 1
    else:
        pass
    return occurrences


def get_length(request):

    if not request.session.get('morethan_n'):
        request.session['morethan_n'] = 3

    if not request.session.get('lessthan_n'):
        request.session['lessthan_n'] = 3

    if not request.session.get('equal_n'):
        request.session['equal_n'] = 3

    if not request.session.get('lengths_words_pos'):
        request.session['lengths_words_pos'] = 'words'

    lengths_words_pos_changed = False
    plusminus = None
    for prop in request.GET:

        if prop == 'words_pos':
            request.session['lengths_words_pos'] = request.GET[prop]
            lengths_words_pos_changed = True

        if prop == 'plusminus':
            if request.GET[prop] == 'plus':
                plusminus = 'plus'
            else:
                plusminus = 'minus'

    set_type = None

    if request.GET.get('type'):
        if request.GET['type'] != 'none':
            set_type = request.GET['type']
            if plusminus == 'plus':
                request.session[request.GET[prop] + '_n'] += 1
            elif plusminus == 'minus':
                if request.session[request.GET[prop] + '_n'] > 1:
                    request.session[request.GET[prop] + '_n'] -= 1

    text_list = get_text_list(request)

    #if not request.session.get('morethan_total'):
    request.session['morethan_total'] = calculate_lengths(text_list, 'morethan', request.session['morethan_n'], request.session['lengths_words_pos'])
    #if not request.session.get('lessthan_total'):
    request.session['lessthan_total'] = calculate_lengths(text_list, 'lessthan', request.session['lessthan_n'], request.session['lengths_words_pos'])
    #if not request.session.get('equal_total'):
    request.session['equal_total'] = calculate_lengths(text_list, 'equal', request.session['equal_n'], request.session['lengths_words_pos'])

    if set_type is not None:
        request.session[set_type + '_total'] = calculate_lengths(text_list, set_type, request.session[set_type + '_n'], request.session['lengths_words_pos'])
    elif lengths_words_pos_changed:
        request.session['morethan_total'] = calculate_lengths(text_list, 'morethan', request.session['morethan_n'], request.session['lengths_words_pos'])
        request.session['lessthan_total'] = calculate_lengths(text_list, 'lessthan', request.session['lessthan_n'], request.session['lengths_words_pos'])
        request.session['equal_total'] = calculate_lengths(text_list, 'equal', request.session['equal_n'], request.session['lengths_words_pos'])

    data = {}
    data['morethan_n'] = request.session['morethan_n']
    data['lessthan_n'] = request.session['lessthan_n']
    data['equal_n'] = request.session['equal_n']

    data['morethan_total'] = request.session['morethan_total']
    data['lessthan_total'] = request.session['lessthan_total']
    data['equal_total'] = request.session['equal_total']

    data['pos_list'] = sorted(list(set([x for sublist in\
    [text.pos_counts.keys() for text in text_list] for x in sublist])))

    if request.session['lengths_words_pos'] == 'words':
        data['words_pos'] = 'Ord'
    else:
        data['words_pos'] = request.session['lengths_words_pos']

    return JsonResponse(data)

def get_metadata(request):
    all_labels = []
    for text in request.session.get('text_list'):
        if text.metadata_labels:
            for label in text.metadata_labels:
                all_labels.append(label)

    metadata_labels = f7(all_labels)
    meta_combos = {}

    for text in request.session.get('text_list'):
        if text.metadata:
            for x in range(len(text.metadata)):
                if text.metadata_labels[x] in meta_combos:
                    if not text.metadata[x] in meta_combos[text.metadata_labels[x]]:
                        meta_combos[text.metadata_labels[x]].append(text.metadata[x])
                else:
                    meta_combos[text.metadata_labels[x]] = [text.metadata[x]]
    return meta_combos

def mean_median_word_len(text_list):
    # Total number of words, their mean and median length
    token_lens = []
    for text in textlist:
        for s in text.sentences:
            for token in s.tokens:
                if token.xpos not in ['MAD', 'MID', 'PAD']:
                    token_lens.append(len(token.norm))
    return round(np.mean(token_lens), 2), round(np.median(token_lens), 2)

def mean_median_sent_len(textlist):
    text_lens = []
    for text in textlist:
        for s in text.sentences:
            text_lens.append(len(s.tokens))
    return round(np.mean(text_lens), 2), round(np.median(text_lens), 2)

def get_general_stats(request):
    if not request.session.get('file_list'):
        return JsonResponse({})

    def mean_median_word_len(textlist):
        token_lens = []
        for text in textlist:
            for s in text.sentences:
                for token in s.tokens:
                    if token.xpos not in ['MAD', 'MID', 'PAD']:
                        token_lens.append(len(token.norm))
        return round(np.mean(token_lens), 2), round(np.median(token_lens), 2)

    def mean_median_sent_len(textlist):
        text_lens = []
        for text in textlist:
            for s in text.sentences:
                text_lens.append(len([t for t in s.tokens if t.xpos not in ['MID','MAD','PAD']]))
        return round(np.mean(text_lens), 2), round(np.median(text_lens), 2)

    stats = {}
    text_list = get_text_list(request)

    non_normalized_files = [f.filename for f in request.session['file_list'] if not f.normalized]
    if not non_normalized_files:
        non_normalized_files = False

    if not text_list:
        return JsonResponse({})

    tokens =    [t.token_count for t in text_list]
    words =     [t.word_count for t in text_list]
    sentences = [t.sentence_count for t in text_list]
    misspells = [t.misspells for t in text_list]
    compounds = [t.compounds for t in text_list]
    paragraphs = [len(t.paragraphs) for t in text_list]


    paragraph_lengths = []
    paragraph_sent_lengths = []

    for t in text_list:
        for p in t.paragraphs:
            paragraph_lengths.append(p)
        for p in t.paragraph_sents:
            paragraph_sent_lengths.append(p)

    stats['n_tokens'] = sum(tokens)
    stats['mean_tokens'] = round(np.mean(tokens), 2)
    stats['median_tokens'] = np.median(tokens)

    stats['mean_word_len'], stats['median_word_len'] = mean_median_word_len(text_list)

    stats['n_words'] = sum(words)
    stats['mean_words'] = round(np.mean(words), 2)
    stats['median_words'] = np.median(words)

    stats['n_sent'] = sum(sentences)
    stats['mean_sent'] = round(np.mean(sentences), 2)
    stats['median_sent'] = np.median(sentences)

    stats['mean_sent_len'], stats['median_sent_len'] = mean_median_sent_len(text_list)

    stats['n_misspells'] = sum(misspells)
    stats['mean_misspells'] = round(np.mean(misspells), 2)
    stats['median_misspells'] = np.median(misspells)

    stats['n_compounds'] = sum(compounds)
    stats['mean_compounds'] = round(np.mean(compounds), 2)
    stats['median_compounds'] = np.median(compounds)

    stats['non_normalized_files'] = non_normalized_files

    stats['n_paragraphs'] = sum(paragraphs)
    stats['mean_paragraphs'] = round(np.mean(paragraphs), 2)
    stats['median_paragraphs']  = np.median(paragraphs)

    stats['mean_paragraph_length'] = round(np.mean(paragraph_lengths), 2)
    stats['median_paragraph_length'] = round(np.median(paragraph_lengths), 2)

    stats['mean_paragraph_sentence_length'] = round(np.mean(paragraph_sent_lengths), 2)
    stats['median_paragraph_sentence_length'] = round(np.median(paragraph_sent_lengths), 2)

    return JsonResponse(stats)

def frequencies(text_list, pos_list, n):
    pass

def pos_stats(text_list, included_pos_tags):
    def perc_string(acc, dp=2):
        # Makes sure there's two decimals
        return ("{0:." + str(dp) + "f}").format(acc * 100) + "%"

    # Change dict merging to rely on Counter(), should make it faster

    pos_stats = {}
    total = 0.0

    for text in text_list:
        for k in text.pos_counts:
            if k in included_pos_tags:
                if k in pos_stats:
                    pos_stats[k] += text.pos_counts[k][0]
                    total += text.pos_counts[k][0]
                else:
                    pos_stats[k] = text.pos_counts[k][0]
                    total += text.pos_counts[k][0]
    d2 = {}
    for k in pos_stats:
        d2[k] = (pos_stats[k], perc_string((pos_stats[k] / total)))

    d2 = list(sorted(d2.items(), key=lambda k: k[1][0], reverse=True))
    return d2

def token_count_text(text):
    tot_tokens = 0

    for line in text.text:
        if len(line.split("\t")) > 4:
            tot_tokens += 1
    return tot_tokens

def word_count_text(text):
    tot_words = 0
    stoplist = ["MAD", "MID", "PAD"]
    for line in text.text:
        if len(line.split("\t")) > 5 and line.split("\t")[6] not in stoplist:
            tot_words += 1
    return tot_words

def avg_word_len_text(text):
    tot_len = 0
    tot_words = 0
    stoplist = ["MAD", "MID", "PAD"]
    for line in text.text:
        if len(line.split("\t")) > 4 and line.split("\t")[6] not in stoplist:
            tot_len += len(line.split("\t")[2])
            tot_words += 1
    return format(round((tot_len/tot_words), 2), '.2f')

def number_of_sentences_text(text):
    no_of_sents = 0
    for line in text.text:
        if len(line.split("\t")) > 5:
            if ":" not in line.split("\t")[2]:
                if line.split("\t")[6] == "MAD":
                    no_of_sents += 1
    if no_of_sents == 0:
        return 1
    return no_of_sents

def avg_sent_len_text(text):
    no_of_sents = number_of_sentences_text(text)
    no_of_tokens = token_count_text(text)

    return format(round((no_of_tokens/no_of_sents), 2), '.2f')

def get_readability(request):
    text_list = get_text_list(request)

    data = {}

    if text_list:
        data['nq_simple_total'], data['nq_full_total'], data['nq_simple_median'], data['nq_full_median'] = nominal_quota(text_list)
        data['ovix_median'], data['ovix_total'], data['ttr_total'], data['ttr_median'] = ovix_ttr(text_list)
        data['lix_median'], data['lix_total'] = lix(text_list)

    return JsonResponse(data)


def misspells_text(text):
    matches = 0
    for line in text.text:
        if len(line.split("\t")) > 3:
            if line.split("\t")[2] != line.split("\t")[3]:
                matches +=1
    return matches

def compound_count_text(text):
    matches = 0
    for line in text.text:
        if len(line.split("\t")) > 1:
            if "-" in line.split("\t")[1]:
                matches += 1
    return matches
