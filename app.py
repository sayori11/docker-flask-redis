from unittest import result
from flask import Flask, redirect, render_template, request, url_for
from tasks import count_words, count_lines, send_mail, q
import smtplib, os, random, string
from werkzeug.utils import secure_filename
from utils import file_allowed, set_task_ids
import redis

r = redis.Redis(host='redis', port=6379)

UPLOAD_FOLDER = './files'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/")
def index():
    if 'key' not in request.args:
        return redirect(url_for('get_key'))
    key = request.args['key']
    tasks=[]
    if r.exists(key):
        task_ids = r.get(key).decode()
        if ', ' not in task_ids:
            tasks = [q.fetch_job(task_ids)]
        else:
            task_ids = task_ids.split(', ')
            tasks = [q.fetch_job(task_id) for task_id in task_ids]
            if None in tasks:
                tasks = [task for task in tasks if task is not None]
    return render_template('index.html', key=key, tasks=tasks)

@app.route("/apikey")
def get_key():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))

@app.route("/scrape", methods=["GET", "POST"])
def scrape():

    key = request.args['key']

    if request.method=="POST":
        url = request.form['url']
        email = request.form['email']

        task = q.enqueue(count_words, url, result_ttl=2000)
        set_task_ids(key, task.id)

        task_mail = q.enqueue_call(func=send_mail, args=(email, task.id), depends_on=task)

        q_len = len(q)

        jobs = q.jobs

        message = f"Task {task.id} queued at {task.enqueued_at.strftime('%a, %d %b %Y %H:%M:%S')}. {q_len} jobs queued"

        return render_template("scrape.html", message=message, task_id=task.id, jobs=jobs, key=key)

    return render_template("scrape.html", key=key)

@app.route('/count-lines', methods=["GET", "POST"])
def count_lines_file():
    key = request.args['key']
    if request.method=="POST":

        file = request.files['text_file']
        if file and file_allowed(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
 
        email = request.form['email']

        task = q.enqueue(count_lines, file_path)

        set_task_ids(key, task.id)

        task_mail = q.enqueue_call(func=send_mail, args=(email, task.id), depends_on=task)

        q_len = len(q)

        jobs = q.jobs

        message = f"Task {task.id} queued at {task.enqueued_at.strftime('%a, %d %b %Y %H:%M:%S')}. {q_len} jobs queued"

        return render_template("file.html", message=message, task_id=task.id, jobs=jobs, key=key)

    return render_template("file.html", key=key)

@app.route("/check-status/<task_id>")
def check_status(task_id):
    task = q.fetch_job(task_id)
    return f'Task:{task.get_status()} Result:{task.result}'

@app.route("/stop-task", methods=["POST"])
def stop_task():
    task_id = request.form['task_id']
    task = q.fetch_job(task_id)
    task.cancel()
    return 'Cancelled'


