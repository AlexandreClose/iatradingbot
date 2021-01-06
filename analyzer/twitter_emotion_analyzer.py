import twint

class TweetAnalyzer:

    def __init__(self):
      t='test'

    def get_tweets_about_symbol( self, symbol ):
        search=''
        if symbol == 'BITCOIN':
            search = "bitcoin OR BITCOIN OR BTC"
        c = twint.Config()
        c.Limit=10
        c.Search = search
        c.Lang = "fr"
        c.Store_json = True
        c.Output = "custom_out.json"
        return twint.run.Search(c)