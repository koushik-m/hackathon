from scripts import scrape
import asyncio
import pytz
from random import randint

from Twper import Query

from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse

from .forms import ScrapeForm
from threading import Thread
from sent_backend.models import Tweet


def index(request):
    return render(request, 'sent_backend/index.html')

def scrape_tweets(request):
    if request.method == 'POST':
#       @asyncio.coroutine
        async def main():
            num = int(request.POST.get('num'))
            if num == 1:
                limit = 10
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
    if request.GET.get('id') and request.GET.get('class'):
        t = Tweet.objects.filter(tweet_id=request.GET.get('id')).first()
        tweet_class = request.GET.get('class')

        if tweet_class == 'negative':
            t.tweet_class = -1
        elif tweet_class == 'neutral':
            t.tweet_class = 0
        elif tweet_class == 'positive':
            t.tweet_class = 1
        elif tweet_class == 'junk':
            t.tweet_class = 2

        t.save()

    unclassified = Tweet.objects.filter(tweet_class=99)
    unclassified_num = len(unclassified)-1
    total_count = Tweet.objects.count()
    msg1 = str(unclassified_num) + " left, " + str(total_count) + " total"
    percent = (total_count - unclassified_num)/total_count*100
    if unclassified_num + 1 == 0:
        return redirect('/backend')
    u = unclassified[randint(0, unclassified_num)]
    context = {'tweet': u, 'msg1': msg1, 'percent': percent}
    return render(request, 'sent_backend/classify.html', context)
