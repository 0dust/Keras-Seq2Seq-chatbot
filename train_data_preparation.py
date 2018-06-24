
import os
import re
import csv
import nltk
import pickle
import operator
import itertools
import numpy as np
import pandas as pd
np.random.seed(2018)
from scipy import sparse, io
from numpy.random import permutation
from keras.preprocessing import sequence



    
questions_file = 'train_data_context.from'
answers_file = 'train_data_reply.to'
vocabulary_file = 'vocabs'
padded_questions_file = 'train_context_padded'
padded_answers_file = 'train_reply_padded'
unknown_token = 'unk'

vocabulary_size = 7000
max_features = vocabulary_size
maxlen_input = 50
maxlen_output = 50  

print ("Reading the context data...")
q = open(questions_file, 'r')
questions = q.read()
print ("Reading the answer data...")
a = open(answers_file, 'r')
answers = a.read()
print ("Tokenizing the answers...")

paragraphs_a = [p for p in answers.split('\n')]
paragraphs_a = ['BOS '+p+' EOS' for p in paragraphs_a]

paragraphs_q = [p for p in questions.split('\n') ]

tokenized_answers = [p.split() for p in paragraphs_a]
tokenized_questions = [p.split() for p in paragraphs_q]

vocab = pickle.load(open(vocabulary_file, 'rb'))


index_to_word = [x[0] for x in vocab]
index_to_word.append(unknown_token)
word_to_index = { w:i for i,w in enumerate(index_to_word)}

print ("Using vocabulary of size %d." % vocabulary_size)
print ("The least frequent word in our vocabulary is '%s' and appeared %d times." % (vocab[-1][0], vocab[-1][1]))

# Replacing all words not in our vocabulary with the unknown token:
for i, sent in enumerate(tokenized_answers):
    tokenized_answers[i] = [w if w in word_to_index else unknown_token for w in sent]
   
for i, sent in enumerate(tokenized_questions):
    tokenized_questions[i] = [w if w in word_to_index else unknown_token for w in sent]

# Creating the training data:
X = np.asarray([[word_to_index[w] for w in sent] for sent in tokenized_questions])
Y = np.asarray([[word_to_index[w] for w in sent] for sent in tokenized_answers])

Q = sequence.pad_sequences(X, maxlen=maxlen_input)
A = sequence.pad_sequences(Y, maxlen=maxlen_output, padding='post')

with open(padded_questions_file, 'w') as q:
    pickle.dump(Q, q)
    
with open(padded_answers_file, 'w') as a:
    pickle.dump(A, a)