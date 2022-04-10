import smtplib, os
import redis

r = redis.Redis(host='redis', port=6379)

ALLOWED_EXTENSIONS = ('txt', 'pdf', 'doc')

def file_allowed(filename):
    return filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def sendMail(message, email):
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    s.login(os.environ['SENDER_EMAIL'], os.environ['SENDER_APP_KEY'])
    s.sendmail(os.environ['SENDER_EMAIL'], email, message)
    s.quit()

def set_task_ids(key, task_id):
    if r.exists(key):
        prev_tasks = r.get(key).decode()
        all_tasks = prev_tasks + ', ' + task_id
        r.set(key, all_tasks)
    else:
        r.set(key, task_id)