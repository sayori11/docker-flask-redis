from flask import Flask, render_template, request
from tasks import count_words, q, r
import smtplib
from rq.command import send_stop_job_command

app = Flask(__name__)

def sendMail(message, email):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login("gsuraj2222@gmail.com", "lgdjeitdinmcphon")
    s.sendmail("gsuraj2222@gmail.com", email, message)
    s.quit()

#Notify by sending email once a task is completed or failed
def success(job, connection, result, *args, **kwargs):
    message = f"Task {job.id} completed! \n Result:{result}"
    sendMail(message)

def failure(job, connection, type, value, traceback):
    message = f"Sorry,Task {job.id} could not be completed"
    sendMail(message)

#Alternately, Notifying by using a dependent function
def send_mail(email, task_id):
    task = q.fetch_job(task_id)

    if task.get_status()=='finished':
        message = f"Task {task_id} completed! \n Result:{task.result}"
        sendMail(message, email)
    else:
        message = f"Sorry,Task {task_id} could not be completed"
        sendMail(message, email)

@app.route("/scrape", methods=["GET", "POST"])
def scrape():

    if request.method=="POST":

        url = request.form["url"]
        email = request.form['email']

        # task = q.enqueue(count_words, url, on_success=success, on_failure=failure)
        task = q.enqueue(count_words, url)
        task_mail = q.enqueue_call(func=send_mail, args=(email, task.id ), depends_on=task)  

        q_len = len(q)

        jobs = q.jobs

        message = f"Task {task.id} queued at {task.enqueued_at.strftime('%a, %d %b %Y %H:%M:%S')}. {q_len} jobs queued"

        return render_template("scrape.html", message=message, task_id=task.id, jobs=jobs)

    return render_template("scrape.html")

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


