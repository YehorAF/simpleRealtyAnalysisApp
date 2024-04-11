import spacy
import os

_core = os.getenv("NLPCORE")

nlp = spacy.load(_core)