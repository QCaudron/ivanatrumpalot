import os
import json
import time
import numpy as np
import pickle
from twitter import Api

users_to_respond = ['BernieSanders', 'HillaryClinton', 'BarackObama', 'WhiteHouse']


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
            return user_tweet_ids
        except:
            return [0 for u in range(len(users_to_respond))]


# Either specify a set of keys here or use os.getenv('CONSUMER_KEY') style
# assignment:
with open('secrets/api_keys', 'rb') as f:
    api_keys = pickle.load(f)

# read in most recent tweet ids from file.
user_tweet_ids = TweetIDs.readIDs()

#setup API
api = Api(api_keys['CONSUMER_KEY'],
          api_keys['CONSUMER_SECRET'],
          api_keys['ACCESS_TOKEN'],
          api_keys['ACCESS_TOKEN_SECRET'])



def respondToUser(twt):
    #respond to user with twt_text as input
    #TODO: put in keras function to generate tweet.
    status = ''
    api.PostUpdate(status,in_reply_to_status_id=twt.id)
    print 'posted "{}" in reply to @{}'.format(status,twt.user.screen_name)

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

if __name__ == '__main__':
    replyIfUpdate()
    TweetIDs.setIDs(user_tweet_ids)
