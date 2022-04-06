import requests
from bs4 import BeautifulSoup
import lxml
import redis
from rq import Queue
import time

r = redis.Redis(host='redis', port=6379, decode_responses=True)
q = Queue(connection=r)

def count_words(url):

    print(f"Counting words at {url}")

    req = requests.get(url)

    soup = BeautifulSoup(req.text, "lxml")

    paragraphs = " ".join([p.text for p in soup.find_all("p")])

    word_count = dict()

    for i in paragraphs.split():
        if not i in word_count:
            word_count[i] = 1
        else:
            word_count[i] += 1

    print(f"Total words: {len(word_count)}")

    return len(word_count)



