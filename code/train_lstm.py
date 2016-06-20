import sys
import re
import numpy as np

from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.layers import LSTM


# This code is heavily influenced by the Keras example code on LSTM for text generation :
# https://github.com/fchollet/keras/blob/master/examples/lstm_text_generation.py


# Read corpus
text = open("trump_corpus").read()

# Encode from unicode, ignoring characters that don't make sense in standard speech
text = unicode(text,errors='ignore')

# Fix a few problems : nuisance characters, new lines, extra spaces...
nuisance_chars = ["\n", "=", "(", ")", "[", "[", "/"]
for char in nuisance_chars:
    text = text.replace(char, "")

# Look for blocks of several capital letters in a row, followed by a colon, and remove them
# These are typically things like "AUDIENCE:"
text = re.sub(r"[A-Z]+:", "", text)

# Corpus length
print("Corpus length : {} characters, approximately {} words.".format(len(text), len(text.split("."))))

# Generate a dictionaries mapping from characters in our alphabet to an index, and the reverse
alphabet = set(text)
alphabet_indices = dict((c, i) for i, c in enumerate(alphabet))
indices_alphabet = dict((i, c) for i, c in enumerate(alphabet))
print("Size of the alphabet : {} characters.".format(len(alphabet))

# Generate sequences of characters that the RNN will use to predict the next character.
primer_length = 60
step = 3
sentences = []
next_character = []
for i in range(0, len(text) - primer_length, step):
    sentences.append(text[i : i + primer_length])
    next_chars.append(text[i + primer_length])
print("Number of sequences generated from the corpus : {}.".format(len(sentences)))

# Vectorise the text sequences : go from N sentences of length primer_length to
# a binary array of size (N, primer_length, alphabet_size). Do the same for the
# next_character array.
print("Vectorising.")
X = np.zeros((len(sentences), primer_length, len(alphabet_size)), dtype=np.bool)
y = np.zeros((len(sentences), len(alphabet)), dtype=np.bool)
for i, sentence in enumerate(sentences):
    for t, char in enumerate(sentence):
        X[i, t, char_indices[char]] = 1
    y[i, char_indices[next_chars[i]]] = 1


# The current model is a four-layer LSTM network with a dropout layer between each hidden layer.
print("Building the model.")
model = Sequential()
model.add(LSTM(128, return_sequences=True, init="glorot_uniform", 
               input_shape=(primer_length, len(alphabet)))
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


# Helper function :
# Sample from a Boltzmann distribution with energies proportional to the probabilities
# returned by the LSTM network, as a function of a temperature parameter
def sample(energies, temperature=1.0):
    energies = np.log(energies) / temperature
    energies = np.exp(energies) / np.sum(np.exp(energies))
    return np.argmax(np.random.multinomial(1, energies))


# Train the model for 250 epochs, outputting some generated text every five iterations
# Save the model every five epochs, just in case training is interrupted
for iteration in range(1, 50):
    print("\n" + "-" * 50)
    print("Iteration", iteration)

    # Train the model for five epochs
    model.fit(X, y, batch_size=128, nb_epoch=5, shuffle=True)

    # Pick a random part of the text to use as a prompt
    start_index = random.randint(0, len(text) - primer_length - 1)

    # For various energies in the probability distribution, 
    # create some 200-character sample strings
    for diversity in [0.2, 0.5, 1.0, 1.2]:
        print("\n----- Diversity : ", diversity)

        generated = ""
        sentence = text[start_index : start_index + primer_length]
        generated += sentence
        print('----- Generating with prompt : "' + sentence + '"')
        sys.stdout.write(generated)

        # Generate 200 characters
        for i in range(200):
            x = np.zeros((1, primer_length, len(chars)))
            for t, char in enumerate(sentence):
                x[0, t, char_indices[char]] = 1.

            predictions = model.predict(x, verbose=0)[0]
            next_index = sample(predictions, diversity)
            next_char = indices_char[next_index]

            generated += next_char
            sentence = sentence[1:] + next_char

            sys.stdout.write(next_char)
            sys.stdout.flush()
        print("\n")

    # Save the model architecture and weights to file
    model.save_weights("weights.h5", overwrite=True)
    with open("model.json", "w") as f:
        f.write(model.to_json())
