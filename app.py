from flask import Flask, request, redirect, url_for, render_template, make_response
import redis

r = redis.Redis(host='redis', port=6379, decode_responses=True)

app = Flask(__name__)

@app.route('/')
def index():
    count = r.incr('count')
    id = request.cookies.get('id')
    if not id:
        id = r.incr('id')
    resp = make_response(f'Hello , This is session no. {id}. This page has been visited {count} times.')
    resp.set_cookie('id', str(id))
    return resp

