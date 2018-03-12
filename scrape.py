from Twper import Query
import asyncio
import pandas as pd
import sys

if len(sys.argv) == 3:
    QUERY, N = sys.argv[1], int(sys.argv[2])
else:
    print("No valid parameters present.")
    sys.exit()

count = 0
SCRAPE_FILE = 'data/scraped.csv'
df = pd.read_csv(SCRAPE_FILE)

async def main():
    global N, count, df, QUERY
    q = Query(QUERY, limit=N)
    async for tw in q.get_tweets():
        fieldnames = {'user': tw.user, 'fullname': tw.fullname, 'tweet_id': tw.tweet_id, 'url': tw.url, 'timestamp': tw.timestamp, 'text': tw.text, 'replies': tw.replies, 'retweets': tw.retweets, 'likes': tw.likes, 'hashtags': tw.hashtags, 'in_train': 0}
        if df[df['tweet_id'] == int(tw.tweet_id)].empty:
            df = df.append(fieldnames, ignore_index=True)
        else:
            count = count + 1

loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(main())
    loop.run_until_complete(loop.shutdown_asyncgens())
finally:
    df.to_csv(SCRAPE_FILE, index=False, header=True)
    print('skipped {}/{} tweets'.format(count, N))
    loop.close()
