import os
import json
import time
import pickle
from datetime import datetime
import random
import logging
import numpy as np
from twitter import Api

from ivanatrumpalot import predict


# Code directory
os.chdir("/root/ivanatrumpalot/code")

# General parameters
logging.basicConfig(level=logging.DEBUG, filename="../model/logs")


my_name = 'ivanatrumpalot'

users_to_respond = ['BernieSanders',
                    'HillaryClinton',
                    'BarackObama',
                    'WhiteHouse']

hash_tags = ['MakeAmericaGreatAgain',
             'Trump2016',
             'AmericaFirst',
             'TrumpDallas',
             'Trump',
             'TrumpTrain']

# Code launch time
now = datetime.now()


# Import the alphabet that was used in training the model.
with open("../model/required_objects.pickle", "rb") as f:
    required_objects = pickle.load(f)
alphabet = required_objects["alphabet"]



class TweetIDs:
    """
    Class for storing and retrieving most recent tweet IDs.
    """

    filename = '../model/user_tweet_ids'

    @staticmethod
    def setIDs(user_tweet_ids):
        with open(TweetIDs.filename, 'wb') as f:
            pickle.dump(user_tweet_ids, f)

    @staticmethod
    def readIDs():
        try:
            with open(TweetIDs.filename, 'rb') as f:
                user_tweet_ids = pickle.load(f)
            for user in users_to_respond: #if added new users
                if user not in user_tweet_ids:
                    user_tweet_ids[user] = 0
            return user_tweet_ids
        except:
            logging.error('couldn\'t open user_tweet_ids.')
            return {user:0 for user in users_to_respond}


# load in api_keys dictionary with keys: CONSUMER_KEY, CONSUMER_SECRET,
# ACCESS_TOKEN, ACCESS_TOKEN_SECRET
with open('../secrets/api_keys', 'rb') as f:
    api_keys = pickle.load(f)



#load dictionary of users had direct messages with, with most recent id.
user_dm_filename = '../model/user_dm_twts'

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
    text = twt.text
    for l in set(text):
        if l not in alphabet:
            text = text.replace(l,' ')

    status = predict(text)
    status = '@' + twt.user.screen_name + ' ' + status
    status += ' #' + random.choice(hash_tags)
    api.PostUpdate(status,in_reply_to_status_id=twt.id)
    print('posted "{}" in reply to @{}'.format(status,twt.user.screen_name))


def randomTweet():

    status = predict(None)
    status += '#' + random.choice(hash_tags)
    api.PostUpdate(status)
    print('posted tweet: {}'.format(status))


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

    # read in most recent tweet ids from file.
    user_tweet_ids = TweetIDs.readIDs()
    for user in users_to_respond:
        cur_twt = findUserTweet(user)
        if cur_twt.id != user_tweet_ids[user]:
            user_tweet_ids[user] = cur_twt.id
            respondToUser(cur_twt)
    TweetIDs.setIDs(user_tweet_ids) #save user_tweet_ids


def replyIfMessaged():

    #reply to message directed at bot.
    user_dm_filename = '../model/user_dm_twts'

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




def catch_and_schedule(f, *args, **kwargs):

    # If it's been more than eight minutes since we started, don't do anything
    # This is to ensure no concurrent API auths are in place
    if (datetime.now() - now).seconds > 480:
        return

    # Otherwise, try the action, logging to file if it fails
    try:
        f(*args, **kwargs)
    except Exception:
        logging.exception("\n\n{}".format(datetime.now()))


if __name__ == '__main__':

    # Reply if we were messaged or mentioned
    catch_and_schedule(replyIfMessaged)

    # Tweet at those we're following
    catch_and_schedule(replyIfUpdate)

    # Random tweet
    if (datetime.now().minute < 5 or datetime.now().minute > 55):
        catch_and_schedule(randomTweet)
