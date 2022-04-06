import time
from flask import Flask, render_template, request, make_response
import redis
from rq import Queue
from tasks import count_words, q

app = Flask(__name__)

@app.route("/scrape", methods=["GET", "POST"])
def scrape():

    message = None

    if request.method=="POST":

        url = request.form["url"]

        task = q.enqueue(count_words, url)  

        q_len = len(q)

        message = f"Task {task.id} queued at {task.enqueued_at.strftime('%a, %d %b %Y %H:%M:%S')}. {q_len} jobs queued"

    return render_template("scrape.html", message=message)

@app.route("/check-status/<task_id>")
def check_status(task_id):
    task = q.fetch_job(task_id)
    return f'Task:{task.get_status()} Result:{task.result}'

