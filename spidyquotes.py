#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run app
"""

import os
import json
import uuid
import random
import string
import base64
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from collections import Counter, defaultdict
from flask_limiter import Limiter


app = Flask(__name__)

app.secret_key = 'yabba dabba doo!'
app.config['SESSION_TYPE'] = 'filesystem'
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
QUOTES = [json.loads(l) for l in open(os.path.join(DATA_DIR, 'quotesdb.jl'))]
ITEMS_PER_PAGE = 10


def quotes_by_author_and_tags():
    authors = defaultdict(lambda: defaultdict(list))
    for quote in QUOTES:
        name = quote.get('author', {}).get('name', '')
        for tag in quote.get('tags', []):
            authors[name][tag].append(quote.get('text'))
    return authors


QUOTES_BY_AUTHOR_AND_TAGS = quotes_by_author_and_tags()


def top_ten_tags():
    tags = (tag for d in QUOTES for tag in d['tags'])
    return Counter(tags).most_common(10)


TOP_TEN_TAGS = top_ten_tags()


def get_quotes_for_page(page, tag=None):
    page = int(page)
    if tag:
        quotes = [q for q in QUOTES if tag in q['tags']]
    else:
        quotes = QUOTES
    start, end = (page - 1) * ITEMS_PER_PAGE, page * ITEMS_PER_PAGE
    has_next_page = len(quotes) > int(page) * ITEMS_PER_PAGE
    return dict(
        quotes=quotes[start:end],
        has_next=has_next_page,
        tag=tag,
        page=page,
    )


@app.route("/")
@app.route("/page/<page>/")
@app.route("/tag/<tag>/")
@app.route("/tag/<tag>/page/<page>/")
def index(tag=None, page=1):
    params = get_quotes_for_page(page=page, tag=tag)
    return render_template('index.html',
                           top_ten_tags=TOP_TEN_TAGS,
                           authenticated='username' in session,
                           **params)


@app.route("/tableful/")
@app.route("/tableful/page/<page>/")
@app.route("/tableful/tag/<tag>/")
@app.route("/tableful/tag/<tag>/page/<page>/")
def tableful(tag=None, page=1):
    params = get_quotes_for_page(page=page, tag=tag)
    return render_template('tableful.html',
                           top_ten_tags=TOP_TEN_TAGS,
                           **params)


@app.route("/js/")
@app.route("/js/page/<page>/")
def data_in_js(page=1):
    params = get_quotes_for_page(page=page)
    params['formatted_quotes'] = json.dumps(params['quotes'], indent=4)
    return render_template('data_in_js.html', **params)


@app.route("/api/quotes")
def api_quotes():
    page = int(request.args.get('page', 1))
    tag = request.args.get('tag')
    data = get_quotes_for_page(page=page, tag=tag)
    data['top_ten_tags'] = TOP_TEN_TAGS
    return jsonify(data)


@app.route("/scroll")
def scroll():
    return render_template('ajax.html')


@app.route("/random")
def random_quote():
    i = random.randrange(0, len(QUOTES))
    return render_template('index.html', quotes=[QUOTES[i]])


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ''
    if request.method == 'POST':
        if not request.form.get('username'):
            error = 'please, provide your username.'
        elif request.form.get('csrf_token') != session.get('csrf_token'):
            error = 'invalid CRSF token.'
        else:
            session['username'] = request.form.get('username')
            return redirect(url_for('index'))
    session['csrf_token'] = ''.join(
        random.sample(string.ascii_letters, len(string.ascii_letters))
    )
    return render_template(
        'login_page.html', csrf_token=session['csrf_token'], error=error
    )


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/search.aspx', methods=['GET'])
def search():
    authors = QUOTES_BY_AUTHOR_AND_TAGS.keys()
    viewstate = base64.b64encode(
        uuid.uuid4().hex.encode('utf-8') + b',' + ','.join(authors).encode('utf-8')
    ).decode('utf-8')
    return render_template(
        'filter.html',
        authors=authors,
        viewstate=viewstate
    )


@app.route('/filter.aspx', methods=['POST'])
def filter():
    selected_author = request.form.get('author')
    viewstate_data = base64.b64decode(request.form.get('__VIEWSTATE')).decode('utf-8').split(',')
    if selected_author not in viewstate_data:
        return redirect(url_for('search'))
    selected_tag = request.form.get('tag')
    if selected_tag:
        viewstate_data.append(selected_tag)
    quotes = QUOTES_BY_AUTHOR_AND_TAGS.get(selected_author, {}).get(selected_tag)
    return render_template(
        'filter.html',
        quotes=quotes,
        selected_author=selected_author,
        selected_tag=selected_tag,
        authors=QUOTES_BY_AUTHOR_AND_TAGS.keys(),
        tags=QUOTES_BY_AUTHOR_AND_TAGS.get(selected_author, {}).keys(),
        viewstate=base64.b64encode(','.join(viewstate_data).encode('utf-8')).decode('utf-8'),
    )


if os.getenv('DYNO'):
    print('running in heroku, enabling limit of 1 request per second...')
    Limiter(app, global_limits=["1 per second"])
else:
    print('NOT running in heroku...')


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--host')
    parser.add_argument('--throttle', action='store_true')
    args = parser.parse_args()
    if args.throttle:
        limiter = Limiter(app, global_limits=["1 per second"])
    app.run(debug=args.debug, host=args.host)
