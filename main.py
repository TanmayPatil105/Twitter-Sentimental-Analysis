import tweepy
import os
import pandas as pd
from tweepy import OAuthHandler
from dotenv import load_dotenv
import regex as re
import csv

#
# fetch tweets using API
#
def scrape():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")   
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuth1UserHandler(
        consumer_key, consumer_secret,
        access_token, access_token_secret
    )

    api = tweepy.API(auth, wait_on_rate_limit=True)


    search_query = "#UkraineVsRussia"
    no_of_tweets = 100

    attributes_container = []

    try:

        columns = ["User", "Date Created", "Followers count", "Number of Likes", "Tweet", "Location", "Verified",  "Retweeted", "Retweet count"]

        for i in range(0,100):

            tweets = api.search_tweets(
                q=search_query, 
                count=no_of_tweets
            )

            for tweet in tweets:

                attributes_container.append([tweet.user.name, 
                                             tweet.created_at, 
                                             tweet.user.followers_count, 
                                             tweet.user.favourites_count,  
                                             tweet.text, tweet.user.location, 
                                             tweet.user.verified, 
                                             tweet.retweeted, 
                                             tweet.retweet_count])
        
        tweets_df = pd.DataFrame(attributes_container)

        tweets_df.to_csv('Dataset.csv', index=False)

    except BaseException as e:
        print('Status Failed On,',str(e))

def preprocess():
    tweets = pd.read_csv('Dataset.csv')

    #processing hashtags
    tweets['hashtag'] = tweets['Tweet'].apply(lambda x: re.findall(r"#(\w+)", x))

    #lowercase
    tweets['tweet_text'] = tweets.Tweet.str.lower()

    #removing hyperlinks
    tweets.Tweet = tweets.Tweet.apply(lambda x: re.sub(r'https?:\/\/\S+', '', x))
    tweets.Tweet.apply(lambda x: re.sub(r"www\.[a-z]?\.?(com)+|[a-z]+\.(com)", '', x))
    tweets.to_csv('Dataset.csv', index=False)

    #remove video links
    tweets.Tweet = tweets.Tweet.apply(lambda x: re.sub(r'{link}', '', x))
    tweets.Tweet = tweets.Tweet.apply(lambda x: re.sub(r"\[video\]", '', x))

    #remove non letter characters
    tweets.Tweet = tweets.Tweet.apply(lambda x: re.sub(r'\W', ' ', x))

    #remove mentions @
    tweets.Tweet = tweets.Tweet.apply(lambda x: re.sub(r'@mention', '', x))

    #remove timestamps in the Date 
    tweets['Date Created'] = tweets['Date Created'].str.split(' ').str[0]

if __name__ == "__main__": 
    load_dotenv()
    scrape()
    preprocess()