#!/usr/bin/env python
# -*- coding: utf-8 -*-

#UPLOAD_LOCATION = "/Users/jesper-nasman/jobb/django/swegram/swegram_main/uploads/"
#PIPE_PATH       = "/Users/jesper-nasman/jobb/django/swegram/swegram_main/annotate/pipeline/"
UPLOAD_LOCATION = "/home/user/swegram/swegram_main/uploads/"
PIPE_PATH       = "/home/user/swegram/swegram_main/annotate/pipeline/"

METADATA_DELIMITER = ' '
METADATA_INITIAL = '<'
METADATA_FINAL = '>'

NO_METADATA_STRING = '(ingen metadata)'

UD_TAGS = [
            'ADJ',
            'ADP',
            'ADV',
            'AUX',
            'CCONJ',
            'DET',
            'INTJ',
            'NOUN',
            'NUM',
            'PART',
            'PRON',
            'PROPN',
            'PUNCT',
            'SCONJ',
            'SYM',
            'VERB',
            'X',
]

SUC_TAGS = [
            'AB',
            'DT',
            'HA',
            'HD',
            'HP',
            'HS',
            'IE',
            'IN',
            'JJ',
            'KN',
            'NN',
            'PC',
            'PL',
            'PM',
            'PN',
            'PP',
            'PS',
            'RG',
            'RO',
            'SN',
            'UO',
            'VB',
]
