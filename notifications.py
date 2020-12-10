import json
import requests
import math
import logging

with open('config.json', 'r') as f:
    config = json.load(f)
    keys = config['API-keys']
    news_key = keys["news"]
    weather_key = keys["weather"]

def get_news(country : str = 'gb', tts : bool = False) -> list:
    ''' Returns a list of the top 10 article titles and their links from newsapi.org'''
    try:
        news_base_url = "https://newsapi.org/v2/top-headlines?"
        complete_url = news_base_url + "country=" + country + "&apiKey=" + news_key
        news = requests.get(complete_url)
        articles = news.json()['articles']
        ten_articles = []
        #print (articles)
        logging.debug("News articles successfully fetched")
        for i in range(10):
            title = articles[i]['title']
            url = articles[i]['url']
            temp = {'title':title, 'url':url}
            ten_articles.append(temp)
        if tts:
            formatted_for_tts = (". Today's top ten news articles are ")
            for i in range(len(ten_articles)):
                formatted_for_tts = (formatted_for_tts + ten_articles[i]['title'] + ". ")
            formatted_for_tts = formatted_for_tts + " Find out more about these articles in the notifications section. "
            return formatted_for_tts
        else:    
            return ten_articles
    except ConnectionError:
        error = ("Connection error while fetching articles, check to see if link is still working or if API is down")
        logging.error(error)
        return error

def get_weather(city : str, country : str, tts : bool = False) -> dict:
    ''' Returns a formatted string with the current weather data for the City/Country provided '''
    try:
        weather_base_url = "http://api.openweathermap.org/data/2.5/weather?q="
        complete_url = weather_base_url + city + "," + country + "&appid=" + weather_key
        weather = requests.get(complete_url)
        condition = weather.json()['weather'][0]['description']
        temp = weather.json()['main']['temp']
        temp = math.floor(float(temp))
        temp -= 273
        logging.debug("Weather data successfully fetched")
        if tts:
            formatted_for_tts = (". Today the weather is "+condition+' , it is '+str(temp)+" degrees. ")
            return formatted_for_tts
        else:
            formatted_str = (str(temp)+'°C, '+condition)
            return formatted_str

    except ConnectionError:
        error = ("Connection error while fetching weather, check to see if link is still working or if API is down")
        logging.error(error)
        return error
def get_covid_data(tts : bool = False) ->dict:
    ''' Returns yesterday's covid data including total cases, cases yesterday, cases today '''
    try:
        URL = ('https://api.coronavirus.data.gov.uk//v1/data?filters=areaType=nation;areaName=england&structure={%22date%22:%22date%22,%22newCasesByPublishDate%22:%22newCasesByPublishDate%22,%22cumCasesByPublishDate%22:%22cumCasesByPublishDate%22,%22newDeathsByDeathDate%22:%22newDeathsByDeathDate%22,%22cumDeathsByDeathDate%22:%22cumDeathsByDeathDate%22}')
        response = requests.get(URL)
        covid_data = response.json()['data']
        today = covid_data[0]
        yesterday  = covid_data[1]
        new_cases_today = today['newCasesByPublishDate']
        new_cases_yesterday = yesterday['newCasesByPublishDate']
        total_cases_so_far = today['cumCasesByPublishDate']
        logging.debug("Covid-19 data successfully fetched")
        if tts:
            formatted_for_tts = ("There have been "+str(new_cases_today)+" new coronavirus cases today in England, up to a total of "+str(total_cases_so_far)+" cases. ")
            return formatted_for_tts
        else:
            formatted_str = (str(new_cases_today)+" new cases today</br>"+str(new_cases_yesterday)+" new cases yesterday</br>"+str(total_cases_so_far)+' total cases so far')
            return formatted_str
    except ConnectionError:
        error = ("Connection error while fetching covid data, check to see if link is still working or if API is down")
        logging.error(error)
        return error        

#print(get_covid_data())
#print(get_weather(city, country))
#print(get_news('gb', True))
