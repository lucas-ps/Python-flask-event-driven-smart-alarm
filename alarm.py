from datetime import datetime
import notifications
import pyttsx3
import json
import logging

with open('config.json', 'r') as f:
    config = json.load(f)
    location = config["location-info"]
    city = location["city"]
    country = location["country"]

engine = pyttsx3.init()

def delay(alarm_time, current_time) -> int:
    """ Calculate the amount of seconds between the current time and the alarm's time """
    difference = alarm_time - current_time
    delay = difference.days * 24 * 60 * 60 + difference.seconds
    return delay

def create_announcment(scheduler, date, time, content, alarm_weather = False, alarm_news = False):
    """ Adds an announcement to the scheduler, also adds weather/news brief if needed """
    current_time = datetime.now()
    alarm_time = datetime.strptime(date + ' ' + time, '%Y-%m-%d %H:%M')
    delay_in_seconds = delay(alarm_time, current_time)
    scheduler.enter(delay_in_seconds, 1, ttsannouncement, (content,))
    logging.info("Alarm for "+date,time+" has been added to scheduler")
    if alarm_weather:
        tts_announcement = notifications.get_weather(city, country, True)
        content = (content + tts_announcement)
        logging.info("Weather brief for "+date,time+" has been added to scheduler")
    if alarm_news:
        tts_announcement = notifications.get_news('gb', True)
        content = (content + tts_announcement)
        logging.info("News brief for "+date,time+" has been added to scheduler")
    scheduler.enter(delay_in_seconds, 1, ttsannouncement, (content,))


def ttsannouncement(content : str):
    """ Makes the TTS announcement """
    try:
        engine.endLoop()
    except RuntimeError:
        logging.warning("Error while using endLoop() for pytts3, there is no currently running loop")
        pass
    engine.say(content)
    engine.runAndWait()
    logging.info("PYTTSx3 successfully output :"+content)
