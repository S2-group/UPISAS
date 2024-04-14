#!/bin/bash

python3 -m nltk.downloader punkt && \
python3 -m nltk.downloader stopwords && \
python3 -m nltk.downloader wordnet
