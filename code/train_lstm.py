import sys
import re
import numpy as np
import json
import pickle

from keras.models import Sequential, model_from_json
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM

from ivanatrumpalot import clean_text, predict, sample


# This code is heavily influenced by the Keras example code on LSTM for text generation :
# https://github.com/fchollet/keras/blob/master/examples/lstm_text_generation.py

# USAGE :
# python train_lstm.py [mode]
# If no arguments are passed, this will train a new model, saving the model's architecture
# to model.json and its weights to weights.h5.
# If [mode] is passed, valid options are "extend" and "predict".
# If the string "extend" is passed, they must be the files saved by train_lstm.py previously.
# If the string "predict" is passed,

# Read and clean corpus
text = clean_text(open("../data/trump_corpus").read())

# Corpus length
print("Corpus : {} characters, approximately {} sentences.".format(len(text), len(text.split("."))))

# Generate a dictionaries mapping from characters in our alphabet to an index, and the reverse
alphabet = set(text)
alphabet_size = len(alphabet)
alphabet_indices = dict((c, i) for i, c in enumerate(alphabet))
indices_alphabet = dict((i, c) for i, c in enumerate(alphabet))
print("Size of the alphabet : {} characters.".format(alphabet_size))

# Generate sequences of characters that the RNN will use to predict the next character.
primer_length = 50
step = 3
sentences = []
next_character = []
for i in range(0, len(text) - primer_length, step):
    sentences.append(text[i : i + primer_length])
    next_character.append(text[i + primer_length])
print("Number of sequences generated from the corpus : {}.".format(len(sentences)))

# Vectorise the text sequences : go from N sentences of length primer_length to
# a binary array of size (N, primer_length, alphabet_size). Do the same for the
# next_character array.
print("Vectorising.")
X = np.zeros((len(sentences), primer_length, alphabet_size), dtype=np.bool)
y = np.zeros((len(sentences), alphabet_size), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        X[i, t, alphabet_indices[char]] = 1
    y[i, alphabet_indices[next_character[i]]] = 1

# Pickle the necessary objects for future prediction
required_objects = { "alphabet" : alphabet,
                     "alphabet_indices" : alphabet_indices,
                     "indices_alphabet" : indices_alphabet,
                     "primer_length" : primer_length
                   }
with open("required_objects.pickle", "wb") as f:
    pickle.dump(required_objects, f)


# The current model is a four-layer LSTM network with a dropout layer between each hidden layer.
print("Building the model.")
model = Sequential()
model.add(LSTM(128, return_sequences=True, init="glorot_uniform",
               input_shape=(primer_length, len(alphabet))))
model.add(Dropout(0.2))
model.add(LSTM(256, return_sequences=True, init="glorot_uniform"))
model.add(Dropout(0.2))
model.add(LSTM(512, return_sequences=True, init="glorot_uniform"))
model.add(Dropout(0.2))
model.add(LSTM(512, return_sequences=False, init="glorot_uniform"))
model.add(Dropout(0.2))
model.add(Dense(len(alphabet)))
model.add(Activation('softmax'))

model.compile(loss='categorical_crossentropy', optimizer='adam')
model.summary()


# Train the model for 250 epochs, outputting some generated text every five iterations
# Save the model every five epochs, just in case training is interrupted
for iteration in range(1, 50):
    print("\n" + "-" * 50)
    print("Iteration {}".format(iteration))

    # Train the model for five epochs
    model.fit(X, y, batch_size=128, nb_epoch=5, shuffle=True)

    # Pick a random part of the text to use as a prompt
    start_index = np.random.randint(0, len(text) - primer_length - 1)

    # For various energies in the probability distribution,
    # create some 200-character sample strings
    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print("\n----- Diversity : ", diversity)

        generated = ""
        sentence = text[start_index : start_index + primer_length]
        generated += sentence
        print("----- Generating with prompt : {}".format(sentence))
        sys.stdout.write(generated)

        # Generate 200 characters
        for i in range(100):
            x = np.zeros((1, primer_length, len(alphabet)))
            for t, char in enumerate(sentence):
                x[0, t, alphabet_indices[char]] = 1.

            predictions = model.predict(x, verbose=0)[0]
            next_index = sample(predictions, diversity)
            next_char = indices_alphabet[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        print("\n")

    # Save the model architecture and weights to file
    model.save_weights("weights.h5", overwrite=True)
    with open("model.json", "w") as f:
        f.write(model.to_json())
