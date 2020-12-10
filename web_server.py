from flask import Flask, render_template, request, redirect, Markup
from datetime import datetime
from alarm import create_announcment, delay
from time import sleep, mktime

import json
import math
import time
import sched
import notifications as api

app = Flask(__name__)
s = sched.scheduler(time.time, time.sleep)

alarms = []
notifications = []

@app.route('/')
def redirect_to_index():
    return redirect('/index')

@app.route('/index')
def index():
    """ Gets data from URL and uses create_announcment() create an annoucment, remove_announcement()
    to remove one from the list, notifications.insert() to add a notification, handles removing notifications, 
    refreshes weather / news / covid data and initialises webpage with necessary parameters. """

    notifications = []

    with open('config.json', 'r') as f:
        config = json.load(f)
        location = config["location-info"]
        city = location["city"]
        country = location["country"]

    ''' Creating a notification for Covid data, weather and news '''
    weather_notification = {"title" : ("Weather in "+city), "content" : api.get_weather(city, country)}
    covid_notification = {"title" : "Coronavirus statistics for England", "content" : Markup(api.get_covid_data())}
    news = api.get_news()
    news_notification = ''
    for i in range(len(news)):
        news_notification = news_notification + '<a href="'+news[i]['url']+'">'+news[i]['title']+'</a></br></br>'
    news_notification = {"title" : "Top news articles", "content" : Markup(news_notification)}

    """ Code for removing items from scheduler queue and corresponding lists """
    try:
        alarm_name = request.args.get("alarm_item")

        for alarm in range(len(alarms)): 
            if alarms[alarm]['title'] == alarm_name: 
                del alarms[alarm] 
                break
        alarm_time = datetime.strptime(str(alarm_name), '%Y-%m-%d %H:%M')
        scheduler_time = int(mktime(alarm_time.timetuple()))
        for event in s.queue:
            if math.ceil(event.time) == scheduler_time:
                s.cancel(event)
                print('Alarm for '+alarm_name+' removed from scheduler')
                
    except ValueError:
        print('No alarm removal parameters provided')
        pass

    notification_name = request.args.get("notif")
    for notification in range(len(notifications)): 
        if notifications[notification]['title'] == notification_name: 
            print ('Notification "'+notification_name+'" has been removed from notification list')
            del notifications[notification] 
            break
    
    notifications.append(weather_notification)
    notifications.append(covid_notification)
    notifications.append(news_notification)

    ''' Code for creating new alarms/notifications '''
    
    s.run(blocking=False)
    alarm_time = request.args.get("alarm")
    alarm_content = request.args.get("two")
    alarm_weather = request.args.get("weather")
    alarm_news = request.args.get("news")

    print (alarm_weather)
    print (alarm_news)

    try:
        time = alarm_time.split("T") [1]
        date = alarm_time.split("T") [0]
        title = alarm_time.replace("T", " ")
        for i in range(len(alarms)):
            if alarms[i]['title'] == title:
                temp = {'title' : 'Unable to create alarm "'+alarm_content+'"','content' :'There was already an alarm set for the time you selected'}
                notifications.insert(0, temp)
                return render_template('index.html', title='CA3 Alarm clock', notifications=notifications, alarms=alarms, image='bingus.jpg')

        temp = {"title" : title, "content" : alarm_content, "weather" : alarm_weather, "news" : alarm_news}  
        create_announcment(s, date, time, alarm_content, alarm_weather, alarm_news)
        alarms.append(temp)    
    except AttributeError:
        print("No alarm creation parameters provided")
        pass

    return render_template('index.html', title='CA3 Alarm clock', notifications=notifications, alarms=alarms, image='image.png')

if __name__ == '__main__':
    app.run()
