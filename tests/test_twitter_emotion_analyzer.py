import unittest

import pytest

from analyzer.twitter_emotion_analyzer import TweetAnalyzer

@pytest.mark.asyncio
def test_get_tweets_about_symbol( ):
    symbol = 'BITCOIN'
    tweetAnalyzer = TweetAnalyzer()
    tweets_df = tweetAnalyzer.get_tweets_about_symbol( symbol )
    print( tweets_df['tweet'] )
    assert len(tweets_df) > 0