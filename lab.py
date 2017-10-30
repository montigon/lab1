import requests

from bs4 import BeautifulSoup

import bottle

import pickle

import math

import sys

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

filename = 'words.pkl'

if __name__ == '__main__' and '-train' not in sys.argv:
    with open(filename, 'rb') as file:
        data = pickle.load(file)

def get_news(HTML_page):
    page = BeautifulSoup(HTML_page, 'html.parser')
    table = page.body.center.table.findAll('tr')[3].td.table
    news = []
    for title, subtext in zip(table.findAll('tr', attrs={"class": "athing"}), table.findAll('td', attrs={"class":"subtext"})):
        t = title.findAll('td', attrs={'class':'title'})[1].a
        piece = {'title':t.string, 'url':t['href']}
        comment = subtext.findAll('a')[-1].string
        if comment == 'discuss':
            piece['comments'] = 0
        elif comment == 'hide':
            for i in ('comments', 'points', 'author'):
                piece[i] = None
            news.append(piece)
            continue
        else:
            piece['comments'] = int(comment.split()[0])
        piece['author'] = subtext.a.string
        piece['points'] = int(subtext.span.string.split()[0])
        news.append(piece)
    return news


Base = declarative_base()
class News(Base):
    __tablename__ = "news"
    ID = Column(Integer, primary_key = True)
    title = Column(String)
    author = Column(String)
    url = Column(String)
    comments = Column(Integer)
    points = Column(Integer)
    label = Column(String)


@bottle.route('/news')
def news_list():
    rows = s.query(News).filter(News.label == None).all()
    a = {'good':[], 'maybe':[], 'never':[]}
    for record in rows:
        label = guess(record.title)
        a[label].append((record, label))

    return bottle.template('news_template', rows=a['good'] + a['maybe'] + a['never'])


def add_words(title, label):
    new_words = get_words(title)
    for word in new_words:
        data[label][1][word] = data[label][1][word] + 1 if word in data[label][1] else 1
    data[label][0] += 1


def train(*labels):
    rows = s.query(News).filter(News.label != None).all()
    empty = {label:[0, {}] for label in labels}
    for row in rows:
        new_words = get_words(row.title)
        for word in new_words:
            empty[row.label][1][word] = empty[row.label][1].get(word, 0) + 1
        empty[row.label][0] += 1
    with open(filename, 'wb') as file:
        pickle.dump(empty, file)
    return empty


def classified(words, data):
    all_clicks = 0
    for label in data:
        all_clicks += data[label][0]

    for label in data:
        label_prob = data[label][0] / all_clicks
        words_prob = 0
        for word in words:
            words_prob += math.log((data[label][1].get(word, 0) + 10 ** -5) / data[label][0])
        yield (math.log(label_prob) + words_prob), label


def guess(title):
    words = get_words(title)
    cl = classified(words, data)
    result = max(cl, key=lambda x:x[0])
    return result[1]


def get_words(title):
    title = title.lower()
    for symbol in '.;:-?!':
        title = title.replace(symbol, ' ')
    return title.split()


@bottle.route('/add_label')
def add_label():
    params = bottle.request.query.dict
    label = params['label'][0]
    ID = int(params['id'][0])
    record = s.query(News).filter(News.ID==ID).first()
    record.label = label
    add_words(record.title, label)
    s.commit()
    bottle.redirect('/news')


@bottle.route('/update_news')
def update_news():
    r = requests.get("https://news.ycombinator.com")
    news = get_news(r.text)
    for piece in news:
        add(piece, s)
    s.commit()
    bottle.redirect('/news')


@bottle.route('/<filename>')
def stylesheets(filename):
    return bottle.static_file(filename, root='./')


def add(record, base):
    query = base.query(News).filter(News.title == record['title'], News.author == record['author'],
        News.url == record['url']).all()
    if not query:
        base.add(News(**record))
    else:
        if query[0].comments != record['comments']:
            query[0].comments = record['comments']
        if query[0].points != record['points']:
            query[0].points = record['points']


if __name__ =='__main__':
    engine = create_engine("sqlite:///news.db")
    Base.metadata.create_all(bind=engine)
    session = sessionmaker(bind=engine)
    s = session()

    r = requests.get("https://news.ycombinator.com")
    news = get_news(r.text)
    for piece in news:
        add(piece, s)
    s.commit()

    if '-train' in sys.argv:
        data = train('good', 'maybe', 'never')
    bottle.run(host='localhost', port=8088)
    
    with open(filename, 'wb') as file:
        pickle.dump(data, file) 