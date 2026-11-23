import spacy
import nltk
from nltk import CFG, ChartParser

nltk.download('punkt')

nlp = spacy.load("en_core_web_sm")

sentence = "The boy eats an apple"

grammar = CFG.fromstring("""
S -> NP VP
NP -> Det N
VP -> V NP
Det -> 'The' | 'an'
N -> 'boy' | 'apple'
V -> 'eats'
""")

parser = ChartParser(grammar)
words = sentence.split()

print("CONSTITUENCY PARSING:")
for tree in parser.parse(words):
    tree.pretty_print()

doc = nlp(sentence)

print("\nDEPENDENCY PARSING:")
for token in doc:
    print(token.text, "-->", token.dep_, "-->", token.head.text)
