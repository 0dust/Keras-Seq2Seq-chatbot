#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 19:02:29 2018

@author: himanshu
"""


import numpy as np
np.random.seed(2018)  # for reproducibility
import itertools
import nltk
import pickle
 

    
questions_file = 'train_data_context.from'
answers_file = 'train_data_reply.to'
vocabulary_file = 'vocabs'

vocabulary_size = 7000

print ("Reading the context data...")
q = open(questions_file, 'r')
questions = q.read()
print ("Reading the answer data...")
a = open(answers_file, 'r')
answers = a.read()
combined = answers + questions
lines = [p for p in combined.split('\n')]

lines = ['BOS '+p+' EOS' for p in lines]
text = ' '.join(lines)
tokenized_text = text.split()


# Counting the word frequencies:

word_freq = nltk.FreqDist(itertools.chain(tokenized_text))
print ("Found %d unique words tokens." % len(word_freq.items()))


vocab = word_freq.most_common(vocabulary_size-1)

# Saving vocabulary:
with open(vocabulary_file, 'w') as v:
    pickle.dump(vocab, v)