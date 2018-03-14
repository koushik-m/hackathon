import csv 
import os
import pandas as pd

fieldnames = ['user', 'fullname', 'tweet_id', 'url', 'timestamp', 'text', 'replies', 'retweets', 'likes', 'hashtags']

df = pd.read_csv('scraped.csv')

df['class'] = 0

no_of_rows = df.shape[0]
count = 1

for index, row in df.iterrows():
    os.system('clear')
    print(' ({}/{}) - {}% completed\n'.format(count, no_of_rows, round((count/no_of_rows)*100, 2)))
    print(row['user'], '\n', "-"*len(row['user']), '\n', row['text'])
    print("\n\n0 = junk (default)")
    print("1 = negative")
    print("2 = neutral")
    print("3 = positive")
    print('9 = discard')
    choice = eval(input())

    df.set_value(index, 'class', choice)

    count = count + 1

df.to_csv('data.csv', index=False, header=True)
