#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run app
"""

import json
import os

from flask import Flask, render_template, request, jsonify
from collections import Counter
from flask_limiter import Limiter


app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
QUOTES = [json.loads(l) for l in open(os.path.join(DATA_DIR, 'quotesdb.jl'))]
ITEMS_PER_PAGE = 10

# PLAN:
# [X] browse by tags
# [X] add top ten tags
# [X] add pagination
# [X] add alternate template with data in JS code
# [X] add alternate template with AJAX UI
# [X] add microdata markup
# [X] add alternate template with tables layout


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
    import time; time.sleep(0.5);
    page = int(request.args.get('page', 1))
    tag = request.args.get('tag')
    data = get_quotes_for_page(page=page, tag=tag)
    data['top_ten_tags'] = TOP_TEN_TAGS
    return jsonify(data)


@app.route("/scroll")
def scroll():
    return render_template('ajax.html')


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
