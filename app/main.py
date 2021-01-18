import os
from flask import Flask, request, url_for, flash, redirect, session, render_template

app = Flask(__name__)
app.config['SECRET_KEY'] = 'CALIWASAMISSIONBUTNOWAGLEAVING'

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route('/')
def index():
    return render_template('base.html', last_updated=dir_last_updated('app/static'))