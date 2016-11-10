from django.conf import settings
from django.contrib.auth import authenticate, login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from twython import Twython
from sklearn.externals import joblib

from thesisdemoproj.DataCleaner import DataCleaner
from dateutil.parser import parse
from thesisdemoproj.POSFeature import POSFeature
from thesisdemoproj.SVM import SVM

CONSUMER_KEY = "6Ou9SSfowTYRYDsQJDX2g6pcV"
CONSUMER_SECRET = "6OT7ybjNe6HL2kKa7SM3hXnW4dwtziWfFroiFHoSwVPV49nRnR"

@csrf_exempt
def auth(request):
    # oauth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    # oauth.set_access_token("2374233954-7qXgGv8iNwm1OHfYDsSNCjFnkE16hLJagKhC4D8", "UFOwbDsong5QuzMflfiTykn6y4mf7ZXf0Bbt5DLf5xxCt")
    # api = tweepy.API(oauth, proxy = "proxy.dlsu.edu.ph:80")
    # public_tweets = api.user_timeline()
    # for tweet in public_tweets:
    #     print (tweet.text)
    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                      client_args={'proxies': {'https': 'http://proxy.dlsu.edu.ph:80'}})

    # Request an authorization url to send the user to...
    callback_url = request.build_absolute_uri(reverse('thesisdemoproj:twitter_callback'))
    auth_props = twitter.get_authentication_tokens(callback_url)

    # Then send them over there, durh.
    request.session['request_token'] = auth_props
    return HttpResponseRedirect(auth_props['auth_url'])


@csrf_exempt
def facebookhandler(request):
    cfl = joblib.load('prototype.pkl')
    svm = SVM()
    dc = DataCleaner()
    print(request.method)
    if request.method == 'POST':
        if 'posts[]' in request.POST:
            f = 0
            m = 0
            posts = request.POST.getlist('posts[]')
            times = request.POST.getlist('time[]')
            for post, time in zip(posts, times):
                date_object = parse(time)
                posFeature = POSFeature(dc.clean_data_facebook(post))
                test = [posFeature.nVerbs, posFeature.nAdjectives]
                res = svm.classifyPersist(cfl, test)
                if (res[0] == 'F'):
                    f += 1
                else:
                    m += 1

            if (f > m):
                return HttpResponse('Female - ' + str(f / (m + f) * 100))
            else:
                return HttpResponse('Male - ' + str(m / (m + f) * 100))  # if everything is OK
    # nothing went well
    return HttpResponse('error')

@csrf_exempt
def thanks(request, redirect_url=settings.LOGIN_REDIRECT_URL):
    oauth_token = request.session['request_token']['oauth_token']
    oauth_token_secret = request.session['request_token']['oauth_token_secret']

    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                      oauth_token, oauth_token_secret,
                      client_args={'proxies': {'https': 'http://proxy.dlsu.edu.ph:80'}})

    authorized_tokens = twitter.get_authorized_tokens(request.GET['oauth_verifier'])

    user = authenticate(
        username=authorized_tokens['screen_name'],
        password=authorized_tokens['oauth_token_secret']
    )
    # login(request, user)

    twitter = Twython(settings.TWITTER_KEY, settings.TWITTER_SECRET,
                      authorized_tokens['oauth_token'], authorized_tokens['oauth_token_secret'],
                      client_args={'proxies': {'https': 'http://proxy.dlsu.edu.ph:80'}})

    user_tweets = twitter.get_user_timeline()

    cfl = joblib.load('prototype.pkl')
    svm = SVM()
    dc = DataCleaner()
    f = 0
    m = 0
    for tweet in user_tweets:
        text = tweet['text']
        posFeature = POSFeature(dc.clean_data_twitter(text))
        test = [posFeature.nVerbs, posFeature.nAdjectives]
        res = svm.classifyPersist(cfl, test)
        if (res[0] == 'F'):
            f += 1
        else:
            m += 1
        # print(tweet['text'])

    print(str(f)+" "+str(m))
    if (f > m):
        return HttpResponseRedirect('/thesisdemoproj?gen=Female&perc='+str(f / (m + f) * 100))
    else:
        return HttpResponseRedirect('/thesisdemoproj?gen=Male&perc='+str(m / (m + f) * 100))
