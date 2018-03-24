import csv
import sys  
import pickle

from collections import Counter
import pandas as pd
from nltk import FreqDist


def analyze_tweet(tweet):
    result = {}
    words = tweet.split()
    result['WORDS'] = len(words)
    bigrams = get_bigrams(words)
    result['BIGRAMS'] = len(bigrams)
    return result, words, bigrams

def get_bigrams(tweet_words):
    bigrams = []
    num_words = len(tweet_words)
    for i in xrange(num_words - 1):
        bigrams.append((tweet_words[i], tweet_words[i + 1]))
    return bigrams


def get_bigram_freqdist(bigrams):
    freq_dict = {}
    for bigram in bigrams:
        if freq_dict.get(bigram):
            freq_dict[bigram] += 1
        else:
            freq_dict[bigram] = 1
    counter = Counter(freq_dict)
    return counter

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: python freq.py <preprocessed-CSV>'
        exit()
    num_tweets, num_pos_tweets, num_neg_tweets = 0, 0, 0
    num_mentions, max_mentions = 0, 0
    num_emojis, num_pos_emojis, num_neg_emojis, max_emojis = 0, 0, 0, 0
    num_urls, max_urls = 0, 0
    num_words, num_unique_words, min_words, max_words = 0, 0, 1e6, 0
    num_junk_tweets, num_neu_tweets, num_neg_tweets, num_pos_tweets = 0, 0, 0, 0
    num_bigrams, num_unique_bigrams = 0, 0
    all_words = []
    all_bigrams = []

    df = pd.read_csv(sys.argv[1])

    for i, row in df.iterrows():
        t_id, if_pos, tweet = row['tweet_id'], row['tweet_class'], row['text']
        # if_pos = int(if_pos)
        if if_pos == 1:
            num_pos_tweets += 1
        elif if_pos == -1:
            num_neg_tweets += 1
        elif if_pos == 0:
            num_neu_tweets += 1
        elif if_pos == 2:
            num_junk_tweets += 1
        result, words, bigrams = analyze_tweet(tweet)
        num_words += result['WORDS']
        min_words = min(min_words, result['WORDS'])
        max_words = max(max_words, result['WORDS'])
        all_words.extend(words)
        num_bigrams += result['BIGRAMS']
        all_bigrams.extend(bigrams)
    unique_words = list(set(all_words))
    with open(sys.argv[1][:-4] + '-unique.txt', 'w') as uwf:
        uwf.write('\n'.join(unique_words))
    num_unique_words = len(unique_words)
    num_unique_bigrams = len(set(all_bigrams))
    print '\nCalculating frequency distribution'
    # Unigrams
    freq_dist = FreqDist(all_words)
    pkl_file_name = sys.argv[1][:-4] + '-freqdist.pkl'
    with open(pkl_file_name, 'wb') as pkl_file:
        pickle.dump(freq_dist, pkl_file)
    print 'Saved uni-frequency distribution to %s' % pkl_file_name
    # Bigrams
    bigram_freq_dist = get_bigram_freqdist(all_bigrams)
    bi_pkl_file_name = sys.argv[1][:-4] + '-freqdist-bi.pkl'
    with open(bi_pkl_file_name, 'wb') as pkl_file:
        pickle.dump(bigram_freq_dist, pkl_file)
    print 'Saved bi-frequency distribution to %s' % bi_pkl_file_name