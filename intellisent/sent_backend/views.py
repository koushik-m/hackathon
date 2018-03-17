from scripts import scrape
import asyncio
import pytz

from Twper import Query

from django.shortcuts import render
from django.http import HttpResponseRedirect

from .forms import ScrapeForm
from threading import Thread
from sent_backend.models import Tweet


def index(request):
    return render(request, 'sent_backend/index.html')

def scrape_tweets(request):
    if request.method == 'POST':
        async def main():
            num = int(request.POST.get('num'))
            if num == 1:
                limit = 500
            elif num == 2:
                limit = 2000
            elif num == 3:
                limit = 10000
            q = Query(request.POST.get('query'), limit=limit)
            async for tw in q.get_tweets():
                clean_tags = ' '.join(tw.hashtags)
                t = Tweet(user=tw.user,
                             fullname=tw.fullname,
                             tweet_id=tw.tweet_id,
                             url=tw.url,
                             timestamp=pytz.timezone('UTC').localize(tw.timestamp),
                             text=tw.text,
                             replies=tw.replies,
                             retweets=tw.retweets,
                             likes=tw.likes,
                             hashtags=clean_tags,
                             tweet_class=99,
                             query=request.POST.get('query'))
                t.save()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(main())
            loop.run_until_complete(loop.shutdown_asyncgens())
        finally:
            loop.close()

        form = ScrapeForm(request.POST)
        if form.is_valid():
            return HttpResponseRedirect('/backend')
    else:
        form = ScrapeForm()
    return render(request, 'sent_backend/scrape.html', {'form': form})

def classify_tweets(request):
    return render(request, 'sent_backend/classify.html')
