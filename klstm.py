import numpy as np
import sys
import pandas as pd
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation
from keras.layers import Embedding
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras.layers import LSTM
from keras.utils import to_categorical
import utils
from keras.preprocessing.sequence import pad_sequences

FREQ_DIST_FILE = 'tweets_new_train-freqdist.pkl'
BI_FREQ_DIST_FILE = 'tweets_new_train-freqdist-bi.pkl'
TRAIN_PROCESSED_FILE = 'tweets_new_train.csv'
TEST_PROCESSED_FILE = 'tweets_new_test.csv'
GLOVE_FILE = 'glove.twitter.27B.25d.txt'
dim = 25

def get_glove_vectors(vocab):
    print 'Looking for GLOVE vectors'
    glove_vectors = {}
    found = 0
    with open(GLOVE_FILE, 'r') as glove_file:
        for i, line in enumerate(glove_file):
            utils.write_status(i + 1, 0)
            tokens = line.split()
            word = tokens[0]
            if vocab.get(word):
                vector = [float(e) for e in tokens[1:]]
                glove_vectors[word] = np.array(vector)
                found += 1
    print '\n'
    print 'Found %d words in GLOVE' % found
    return glove_vectors


def get_feature_vector(tweet):
    words = tweet.split()
    feature_vector = []
    for i in range(len(words) - 1):
        word = words[i]
        if vocab.get(word) is not None:
            feature_vector.append(vocab.get(word))
    if len(words) >= 1:
        if vocab.get(words[-1]) is not None:
            feature_vector.append(vocab.get(words[-1]))
    return feature_vector


def process_tweets(csv_file, test_file=True):
    tweets = []
    labels = []
    print 'Generating feature vectors'
    df = pd.read_csv(csv_file)

    def get_info(text, tweet_class):
    	feature_vector = get_feature_vector(text)
    	if test_file:
    		tweets.append(feature_vector)
    	else:
    		tweets.append(feature_vector)
    		labels.append(tweet_class)

	# df['clean']  = df.apply(lambda x: clean_tweets(x['text'], x['query']), axis=1)

    df.apply(lambda row: get_info(row['text'], row['tweet_class']), axis=1)

    return tweets, np.array(labels)


if __name__ == '__main__':
    train = len(sys.argv) == 1
    np.random.seed(1337)
    vocab_size = 90000
    batch_size = 500
    max_length = 40
    filters = 600
    kernel_size = 3
    vocab = utils.top_n_words(FREQ_DIST_FILE, vocab_size, shift=1)
    glove_vectors = get_glove_vectors(vocab)

    tweets, labels = process_tweets(TRAIN_PROCESSED_FILE, test_file=False)
    embedding_matrix = np.random.randn(vocab_size + 1, dim) * 0.01
    for word, i in vocab.items():
        glove_vector = glove_vectors.get(word)
        if glove_vector is not None:
            embedding_matrix[i] = glove_vector
    tweets = pad_sequences(tweets, maxlen=max_length, padding='post')
    shuffled_indices = np.random.permutation(tweets.shape[0])
    tweets = tweets[shuffled_indices]
    labels = labels[shuffled_indices]
    if train:
        model = Sequential()
        model.add(Embedding(vocab_size + 1, dim, weights=[embedding_matrix], input_length=max_length))
        model.add(Dropout(0.4))
        model.add(LSTM(128))
        model.add(Dense(64))
        model.add(Dropout(0.5))
        model.add(Activation('relu'))
        model.add(Dense(4))
        model.add(Activation('sigmoid'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        filepath = "./models/lstm-{epoch:02d}-{loss:0.3f}-{acc:0.3f}-{val_loss:0.3f}-{val_acc:0.3f}.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor="loss", verbose=1, save_best_only=True, mode='min')
        reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=2, min_lr=0.000001)
        print model.summary()

        transformed_labels = to_categorical(labels)

        model.fit(tweets, transformed_labels, batch_size=128, epochs=5, validation_split=0.1, shuffle=True, callbacks=[checkpoint, reduce_lr])
    else:
        model = load_model(sys.argv[1])
        print model.summary()
        text = pd.read_csv(TEST_PROCESSED_FILE)
        text = text['text']
        test_tweets, _ = process_tweets(TEST_PROCESSED_FILE, test_file=True)
        test_tweets = pad_sequences(test_tweets, maxlen=max_length, padding='post')
        predictions = model.predict(test_tweets, batch_size=128, verbose=1)
        # results = zip(map(str, range(len(test_tweets))), np.round(predictions[:, 0]).astype(int))
        results = zip(map(str, range(len(test_tweets))), predictions)
        # utils.save_results_to_csv(results, 'lstm.csv')
        with open('lstm.csv', 'w') as csv:
	        csv.write('id,text,prediction\n')
	        for i in range(len(results)):
	            csv.write(results[i][0])
	            csv.write(',')
	            csv.write(text.iloc[i])
	            csv.write(',')
	            csv.write(str(results[i][1]))
	            csv.write('\n')