from tokenize import String
import requests
import re
from datetime import date, time
from bs4 import BeautifulSoup
import datetime as dt

# ссылка на архив
URL_ARCHIVE = "https://apod.nasa.gov/apod/archivepix.html"

# base url need to append YYMMDD
BASE_URL = "https://apod.nasa.gov/apod/"


def get_page(url):
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


soup = get_page(URL_ARCHIVE)


class DateOutOfRangeException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def reformat_date(date):
    s = ([str(s) for s in re.findall(r'\d\d', date)])
    s = ([str(s) for s in re.findall(r'\d\d', date)])
    curDate = dt.datetime.now()
    try:
        trgDate = dt.datetime(2000 + int(s[2]), int(s[1]), int(s[0]))
        print(trgDate)
    except:
        raise DateOutOfRangeException("Bad Date Format")
    if (trgDate > curDate):
        raise  DateOutOfRangeException("Date can't be more than current date")
    if (trgDate < dt.datetime(2015, 1, 1)):
        raise  DateOutOfRangeException("Date can't be less than 2015 01 01")
    return s[2] + s[1] + s[0]


def find_picture_by_date(date):
    to_find = reformat_date(date)
    for ref in soup.find_all('a'):
        if (to_find in ref['href']):
            url = BASE_URL + ref['href']
    return get_picture_from_page(get_page(url))


class Picture:
    url = None
    description = None
    name = None
    date = None

    def __init__(self, url, description, name, date) -> None:
        self.url = url + "?0"
        self.description = description
        self.name = name
        self.date = date

    def __str__(self):
        return self.url + '\n' + \
               self.name + '\n' + \
               self.date + '\n' + \
               self.description


def get_description(rsp):
    descr = rsp.find_all('p')[2]
    descr = "".join(descr.find_all(text=True))
    descr = re.split('Tomorrow\'s picture|Explore Your Universe', descr)
    descr = "".join(descr[0])
    descr = descr.replace('\n', " ").replace(' Explanation:', '').replace('  ', ' ').replace('  ', ' ').strip()
    return descr


def get_picture_from_page(rsp):
    curr_pict_link = ''
    for e in rsp.find_all('a'):
        if e:
            if 'image' in e['href']:
                curr_pict_link = e['href']
                break

    picture_name = rsp.find_all('center')[1].b.text
    picture_link = "https://apod.nasa.gov/apod/" + curr_pict_link
    picture_date = rsp.center.find_all('p')[1].text.replace("\n", '')
    picture_description = get_description(rsp)
    return Picture(picture_link, picture_description, picture_name, picture_date)


def get_time():
    return str(dt.datetime.now())


def get_apod():
    rsp = get_page(BASE_URL)
    return get_picture_from_page(rsp)
