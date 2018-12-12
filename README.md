### Installing

There are two repositories included in swegram that need to be acquired separately:

UDpipe (https://github.com/ufal/udpipe), where the executable should be available in swegram_main/handle_texts/pipeline/nlp/udpipe/udpipe
efselab (https://github.com/robertostling/efselab), along with the Swedish annotation pipeline, for which instructions can be found in the readme for efselab. The swedish pipeline should be available in swegram_main/handle_texts/pipeline/nlp/efselab/swe_pipeline.py

### Configuring

swegram/base.py contains settings that are typically shared between production and development environments. It then imports the appropriate configuration, either local.py or production.py. production.py is not included in the repository; just make a copy of local.py and change the appropriate settings (DEBUG, PRODUCTION, SECRET_KEY etc).

