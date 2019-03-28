from textblob import TextBlob
import re
import nltk


def clean_text(text):
    text = text.lower()
    text = re.sub('\W+', ' ', text)
    return text

def get_sentiment(text):
    analysis = TextBlob(text)
    # set sentiment
    if analysis.sentiment.polarity > 0:
        return 'positive'
    elif analysis.sentiment.polarity == 0:
        return 'neutral'
    else:
        return 'negative'

def add_sentiments(df, columnname):
    df[columnname] = df[columnname].apply(lambda x: clean_text(x))
    sentimentlist = []
    for i in df[columnname]:
        sentiment = get_sentiment(i)
        sentimentlist.append(sentiment)
    df['sentiment'] = sentimentlist
    return df



