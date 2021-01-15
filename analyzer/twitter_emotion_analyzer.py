import twint
from textblob import TextBlob

class TweetAnalyzer:

    def __init__(self):
      t='test'

    def get_tweets_about_symbol( self, symbol ):
        search=''
        if symbol == 'BITCOIN':
            search = "bitcoin OR BITCOIN OR BTC"
        c = twint.Config()
        c.Search = search
        c.Lang = "en"
        c.Limit = 100
        c.Store_json = True
        c.Pandas = True
        c.Hide_output = True
        twint.run.Search(c)
        tweets_df = twint.storage.panda.Tweets_df
        return tweets_df