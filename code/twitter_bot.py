import os
import json
from twitter import Api
import time
import numpy as np
import pickle
import datetime
import random
from ivanatrumpalot import predict

my_name = 'ivanatrumpalot'

users_to_respond = ['BernieSanders',
         'HillaryClinton',
         'BarackObama',
         'WhiteHouse']

hash_tags = ['MakeAmericaGreatAgain', 'Trump2016', 'AmericaFirst', 'TrumpDallas', 'Trump', 'TrumpTrain']

class TweetIDs:
    #class for storing and retrieving most recent tweet IDs for all users being
    filename = 'user_tweet_ids'
    @staticmethod
    def setIDs(user_tweet_ids):
        with open(TweetIDs.filename, 'wb') as f:
            pickle.dump(user_tweet_ids, f)
    @staticmethod
    def readIDs():
        try:
            with open(TweetIDs.filename, 'rb') as f:
                user_tweet_ids = pickle.load(f)
            if len(user_tweet_ids) != len(users_to_respond): #if added new users.
                new_ids = []
                for i,user in enumerate(users_to_respond):
                    if i < len(user_tweet_ids):
                        new_ids.append(user_tweet_ids[i])
                    else:
                        new_ids.append(0)
                user_tweet_ids = new_ids
            return user_tweet_ids
        except:
            return [0 for u in range(len(users_to_respond))]
# load in api_keys dictionary with keys: CONSUMER_KEY, CONSUMER_SECRET,
# ACCESS_TOKEN, ACCESS_TOKEN_SECRET
with open('../secrets/api_keys', 'rb') as f:
    api_keys = pickle.load(f)



# read in most recent tweet ids from file.
user_tweet_ids = TweetIDs.readIDs()

#load dictionary of users had direct messages with, with most recent id.
user_dm_filename = 'user_dm_twts'

try:
    with open(user_dm_filename,'rb') as f:
        user_dm_twts = pickle.load(f)
except:
    user_dm_twts = {}

#setup API
api = Api(api_keys['CONSUMER_KEY'],
          api_keys['CONSUMER_SECRET'],
          api_keys['ACCESS_TOKEN'],
          api_keys['ACCESS_TOKEN_SECRET'])


def respondToUser(twt):
    #respond to user with twt_text as input

    status = predict(twt.text)
    status += '#' + random.choice(hash_tags)
    api.PostUpdate(status,in_reply_to_status_id=twt.id)
    print 'posted "{}" in reply to @{}'.format(status,twt.user.screen_name)

def randomTweet():

    status = predict()
    status += '#' + random.choice(hash_tags)
    api.PostUpdate(status)
    print 'posted tweet: {}'.format(status)

def findUserTweet(user):
    #finds most recent tweet from user
    res = api.GetSearch(
    raw_query="q=from%3A{}&result_type=recent&count=1".format(user))
    return res[0]

def setUserTweetIDs(users):
    #find most comon tweets for users and return as array.
    ids = []
    for i,user in enumerate(users):
        ids.append(findUserTweetID(user))
    return ids

def replyIfUpdate():
    # for each user to respond to, check if most recent tweet ID is
    # the same as tweet already stored. If not then respond to user.
    for i,user in enumerate(users_to_respond):
        cur_twt = findUserTweet(user)
        if cur_twt.id != user_tweet_ids[i]:
            user_tweet_ids[i] = cur_twt.id
            respondToUser(cur_twt)

def replyIfMessaged():
    #reply to message directed at bot.
    user_dm_filename = 'user_dm_twts'
    #load dictionary of users had direct messages with, with most recent id.
    try:
        with open(user_dm_filename,'rb') as f:
            user_dm_twts = pickle.load(f)
    except:
        user_dm_twts = {}

    #get 100 most recent messages addressed to my_name.
    tweets = api.GetSearch(
    raw_query="q=to%3A{}&result_type=recent&count=100".format(my_name))
    all_user_names = [] #keep list of users replied to in this round to ensure only reply to most recent message.


    for twt in tweets:
        screen_name = twt.user.screen_name

        if  screen_name not in user_dm_twts and screen_name not in all_user_names:
            #if never replied to and screen_name not in list of responses.
            respondToUser(twt)
            user_dm_twts[screen_name] = twt.id
            all_user_names.append(screen_name)
        elif user_dm_twts[screen_name] != twt.id and screen_name not in all_user_names:
            #if tweet hasn't been responded to then respond.
            respondToUser(twt)
            user_dm_twts[screen_name] = twt.id
            all_user_names.append(screen_name)
        elif screen_name not in all_user_names:
            all_user_names.append(screen_name)
        #save updated list
        with open(user_dm_filename, 'wb') as f:
                pickle.dump(user_dm_twts, f)

if __name__ == '__main__':
    #reply to user if they have updated tweet and update tweet ids.
    replyIfUpdate()
    TweetIDs.setIDs(user_tweet_ids)
    #If within ten minutes of the hour tweet
    now = datetime.datetime.now()
    if (now.minute<5 or now.minute>55):
        randomTweet()
    #respond to messages addressed to bot
    replyIfMessaged()
