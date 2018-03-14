from Twper import Query
import asyncio
import pandas as pd
import sys
from sent_backend.models import Tweet
import threading

def make_query(QUERY, N):
    async def main():
        loop = asyncio.new_event_loop()
        q = Query(QUERY, limit=N)
        def async_tweets():
            for tw in q.get_tweets():
                if not Tweet.objects.filter(tweet_id=tw.tweet_id).exists():
                    clean_tags = ' '.join(tw.hashtags)
                    t = Tweet(user=tw.user,
                             fullname=tw.fullname,
                             tweet_id=tw.tweet_id,
                             url=tw.url,
                             timestamp=tw.timestamp,
                             text=tw.text,
                             replies=tw.replies,
                             retweets=tw.retweets,
                             likes=tw.likes,
                             hashtags=clean_tags,
                             tweet_class=99)
                    t.save()
        future = loop.run_in_executor(None, async_tweets)
        response = await future
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
    loop.close()
