import unittest
import json
from analyzer.twitter_emotion_analyzer import TweetAnalyzer

class TestTweetAnalyzer(unittest.TestCase):

    def test_get_tweets_about_symbol(self ):
        symbol = 'BITCOIN'
        tweetAnalyzer = TweetAnalyzer()
        tweetAnalyzer.get_tweets_about_symbol( symbol )
        with open('custom_out.json', 'r') as f:
            tweets = json.load(f)
            self.assertEqual(len(tweets), 100)

if __name__ == '__main__':
    unittest.main()