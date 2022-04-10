import requests
from bs4 import BeautifulSoup
import lxml
import redis
from rq import Queue
import time
from utils import sendMail

r = redis.Redis(host='redis', port=6379)
q = Queue(connection=r)

def count_words(url):

    time.sleep(20)

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

def count_lines(file_path):
    time.sleep(10)
    with open(file_path, "r") as f:
        count = len(f.readlines())

    print(f"Total lines: {count}")

    return count

def send_mail(email, task_id):
    task = q.fetch_job(task_id)

    if task.get_status()=='finished':
        message = f"Task {task_id} completed! \n Result:{task.result}"
    else:
        message = f"Sorry,Task {task_id} could not be completed"

    sendMail(message, email)

def check_tasks():
    while True:
        print('Checking')
        print(f'Queue length: {len(q)}')
        for job in q.jobs:
            if job.result:
                print(f'{job.id}\n Result:{job.result}')
        time.sleep(10)

if __name__ == '__main__':
    check_tasks()




