import unittest
from analyzer.twitter_emotion_analyzer import TweetAnalyzer

class TestTweetAnalyzer(unittest.TestCase):

    def test_get_tweets_about_symbol(self ):
        symbol = 'BITCOIN'
        tweetAnalyzer = TweetAnalyzer()
        tweets_df = tweetAnalyzer.get_tweets_about_symbol( symbol )
        print( tweets_df['tweet'] )
        self.assertGreater( len(tweets_df), 0)

if __name__ == '__main__':
    unittest.main()