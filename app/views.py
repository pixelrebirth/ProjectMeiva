from app import app
from flask import render_template

@app.route('/')
@app.route('/index')
def index():
    categories = [{'name': 'thing', 'stuff': 'mabob'},{'name': 'thing2', 'stuff': 'mabob2'}]
    return render_template('index.html',
                           title='Home',
                           categories = categories
    )
