NB: This is a personal copy of jespernasman/swegram

### Installing

There are two modules that need to be aquired separately:

`UDpipe` (http://ufal.mff.cuni.cz/udpipe), where the executable should be available in swegram_main/handle_texts/pipeline/nlp/udpipe/udpipe. It makes use of an English model, the default path is nlp/udpipe/en/english-ud-2.0-170801.udpipe.

`efselab` (https://github.com/robertostling/efselab), along with the Swedish annotation pipeline, for which instructions can be found in the readme for efselab. The swedish pipeline should be available in swegram_main/handle_texts/pipeline/nlp/efselab/swe_pipeline.py

### Configuring

swegram/base.py contains settings that are typically shared between production and development environments. It then imports the appropriate configuration, either local.py or production.py. production.py is not included in the repository; just make a copy of local.py and change the appropriate settings (`DEBUG`, `PRODUCTION`, `SECRET_KEY` etc.). The paths in `swegram_main/config.py` also need to be changed. 

The templates, `swegram_main/templates/`, and `swegram_main/views.py` contain a few hardcoded URLs, the easiest way would be to search all of them for "swegram" and replace them.

A database is required, local.py is configured to use postgres.

By default, LocMemCache is used for caching (for development purposes), this should be changed to DatabaseCache (or redis, but that's pretty overkill)

Remember to check requirements.txt and install anything that's missing. 
