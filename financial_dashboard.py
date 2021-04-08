import streamlit as st
#import yfinance as yf 
import pandas as pd
import numpy as np
import requests
import tweepy
import datetime as dt
import datetime
import config 
import sys
import random
import plotly.graph_objects as go
import plotly.express as px
from client import AlphaVantageClient
from plotly.subplots import make_subplots
from alpha_vantage.timeseries import TimeSeries
from PIL import Image
from utils import data_cleaner, financial_statement_chart, quotes_chart, local_css
from wordcloud import WordCloud
from ta.volatility import BollingerBands
from ta.trend import MACD
from ta.momentum import RSIIndicator
yf.pdr_override()

auth = tweepy.OAuthHandler(configtweets.TWITTER_CONSUMER_KEY, configtweets.TWITTER_CONSUMER_SECRET)
auth.set_access_token(configtweets.TWITTER_ACCESS_TOKEN,configtweets.TWITTER_ACCESS_TOKEN_SECRET)

api = tweepy.API(auth)

snp500 = pd.read_csv("constituents-financials_csv.csv")
symbols = snp500['Symbol'].sort_values().tolist() 
st.title('Financial Dashboard web app')

st.write('With this web application  you will be able to view basic fundamental analysis from all the S&P500 stocks display all the mentions of a stock symbol on Stocktwitts ,and finally technical financial analysis of different companies.')


st.sidebar.write('Financial Analysis option')
image = Image.open('160-1606133_financial-graph-on-technology-abstract-background-picture-stock.jpg')
st.image(image,use_column_width=True)

#option of the sidebar 
option = st.sidebar.selectbox("Choose your analysis option", ('Fundamental financial analysis', 'Sentiment Analysis','Technical financial analysis'), 0)

st.header(option)

def app():
    raw_text = st.text_area("Enter the exact twitter handle of the Personality (without @)")

if option == 'Fundamental financial analysis' : 
    ticker = st.sidebar.selectbox(
    'Choose a S&P 500 Stock',
     symbols)
    stock = yf.Ticker(ticker)
    info = stock.info 
    st.title('Company Profile')
    st.subheader(info['longName']) 
    st.markdown('** Sector **: ' + info['sector'])
    st.markdown('** Industry **: ' + info['industry'])
    st.markdown('** Phone **: ' + info['phone'])
    st.markdown('** Address **: ' + info['address1'] + ', ' + info['city'] + ', ' + info['zip'] + ', '  +  info['country'])
    st.markdown('** Website **: ' + info['website'])
    st.markdown('** Business Summary **')
    st.info(info['longBusinessSummary'])
        
    fundInfo = {
            'Enterprise Value (USD)': info['enterpriseValue'],
            'Enterprise To Revenue Ratio': info['enterpriseToRevenue'],
            'Enterprise To Ebitda Ratio': info['enterpriseToEbitda'],
            'Net Income (USD)': info['netIncomeToCommon'],
            'Profit Margin Ratio': info['profitMargins'],
            'Forward PE Ratio': info['forwardPE'],
            'PEG Ratio': info['pegRatio'],
            'Price to Book Ratio': info['priceToBook'],
            'Forward EPS (USD)': info['forwardEps'],
            'Beta ': info['beta'],
            'Book Value (USD)': info['bookValue'],
            'Dividend Rate (%)': info['dividendRate'], 
            'Dividend Yield (%)': info['dividendYield'],
            'Five year Avg Dividend Yield (%)': info['fiveYearAvgDividendYield'],
            'Payout Ratio': info['payoutRatio']
        }
    
    fundDF = pd.DataFrame.from_dict(fundInfo, orient='index')
    fundDF = fundDF.rename(columns={0: 'Value'})
    st.subheader('Fundamental Info') 
    st.table(fundDF)
    
    st.subheader('General Stock Info') 
    st.markdown('** Market **: ' + info['market'])
    st.markdown('** Exchange **: ' + info['exchange'])
    st.markdown('** Quote Type **: ' + info['quoteType'])
    
    start = dt.datetime.today()-dt.timedelta(2 * 365)
    end = dt.datetime.today()
    df = yf.download(ticker,start,end)
    df = df.reset_index()
    fig = go.Figure(
            data=go.Scatter(x=df['Date'], y=df['Adj Close'])
        )
    fig.update_layout(
        title={
            'text': "Stock Prices Over Past Two Years",
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'})
    st.plotly_chart(fig, use_container_width=True)
    
    marketInfo = {
            "Volume": info['volume'],
            "Average Volume": info['averageVolume'],
            "Market Cap": info["marketCap"],
            "Float Shares": info['floatShares'],
            "Regular Market Price (USD)": info['regularMarketPrice'],
            'Bid Size': info['bidSize'],
            'Ask Size': info['askSize'],
            "Share Short": info['sharesShort'],
            'Short Ratio': info['shortRatio'],
            'Share Outstanding': info['sharesOutstanding']
    
        }
    
    marketDF = pd.DataFrame(data=marketInfo, index=[0])
    st.table(marketDF)

if option == 'Sentiment Analysis':
    if st.checkbox('Trendings on StockTwits'):
        
            st.write('StockTwits is a social media platform designed for sharing ideas between investors, traders, and entrepreneurs.This app allows you to  display the mention of a stock symbol on Stocktwitts : ')
            symbol = st.text_input("Enter your symbol", value='AAPL', max_chars=10)
            r=requests.get(f"https://api.stocktwits.com/api/2/streams/symbol/{symbol}.json")
            image = Image.open("stocktwits-logo.jpg")
            st.image(image,use_column_width=True)

            data = r.json()

            for message in data['messages']:
                st.image(message['user']['avatar_url'])
                st.write(message['user']['username'])
                st.write(message['created_at'])
                st.write(message['body'])

    if st.checkbox('Trendings on Twitter'):
        image = Image.open("Twitter-Hole-featured.jpg")
        st.image(image,use_column_width=True)
        st.write('View tweets about stocks from popular traders on Twitter.')
        for username in configtweets.TWITTER_USERNAMES:
            user = api.get_user(username)
            tweets = api.user_timeline(username)

            st.subheader(username)
            st.image(user.profile_image_url)

            for tweet in tweets:
                if '$' in tweet.text:
                    words = tweet.text.split(' ')
                    for word in words : 
                        if word.startswith('$') and word[1:].isalpha():
                            symbol = word[1:]
                            st.write(tweet.text)
                            st.image(f"https://charts2.finviz.com/chart.ashx?t={symbol}")


if option == 'Technical financial analysis':
    st.sidebar.header('User Input Parameters')

    today = datetime.date.today()
    def user_input_features():
        ticker = st.sidebar.text_input("Enter the company Ticker", 'MSFT')
        start_date = st.sidebar.text_input("Start Date", '2019-01-01')
        end_date = st.sidebar.text_input("End Date", f'{today}')
        return ticker, start_date, end_date

    symbol, start, end = user_input_features()

    def get_symbol(symbol):
        url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc?query={}&region=1&lang=en".format(symbol)
        result = requests.get(url).json()
        for x in result['ResultSet']['Result']:
            if x['symbol'] == symbol:
                return x['name']
    company_name = get_symbol(symbol.upper())

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # Read data 
    data = yf.download(symbol,start,end)

    # Bollinger Bands
    indicator_bb = BollingerBands(data['Close'])
    bb = data
    bb['bb_h'] = indicator_bb.bollinger_hband()
    bb['bb_l'] = indicator_bb.bollinger_lband()
    bb = bb[['Close','bb_h','bb_l']]

    # Plot the prices and the bolinger bands
    st.subheader('Stock Bollinger Bands')
    st.line_chart(bb)
    st.write('Bollinger Bands are a technical analysis tool developed by John Bollinger in the 1980s for trading stocks.')
    st.write('The bands comprise a volatility indicator that measures the relative high or low of a security’s price in relation to previous trades.')
    st.write('Bollinger Bands can be used to determine how strongly an asset is rising and when it is potentially reversing or losing strength. If an uptrend is strong enough, it will reach the upper band regularly. An uptrend that reaches the upper band indicates that the stock is pushing higher and traders can exploit the opportunity to make a buy decision. If the price pulls back within the uptrends, and it stays above the middle band and moves back to the upper band, that indicates a lot of strength. Generally, a price in the uptrend should not touch the lower band, and if it does, it is a warning sign for a reverse or that the stock is losing strength.')
    st.write('Bollinger Bands can be used to determine how strongly an asset is falling and when it is potentially reversing to an upside trend. In a strong downtrend, the price will run along the lower band, and this shows that selling activity remains strong. But if the price fails to touch or move along the lower band, it is an indication that the downtrend may be losing momentum. When there are price pullbacks (highs), and the price stays below the middle band and then moves back to the lower band, it is an indication of a lot of downtrend strength. In a downtrend, prices should not break above the upper band since this would indicate that the trend may be reversing, or it is slowing.')
    st.write('Many traders avoid trading during downtrends, other than looking for an opportunity to buy when the trend begins to change. The downtrend can last for short or long durations – either minutes, hours, weeks, days, months, or even years. Investors must identify any sign of downtrends early enough to protect their investments. If the lower bands show a steady downtrend, traders must be cautious to avoid entering into long trades that will prove unprofitable.')




