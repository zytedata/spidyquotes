#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Run app
"""

import json
import os

from flask import Flask, render_template
from collections import Counter


app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
QUOTES = [json.loads(l) for l in open(os.path.join(DATA_DIR, 'quotesdb.jl'))]
ITEMS_PER_PAGE = 10
TABLEFUL_MODE = False

# PLAN:
# [X] browse by tags
# [X] add top ten tags
# [X] add pagination
# [ ] add alternate template with data in JS code
# [ ] add alternate template with AJAX UI
# [ ] add microdata markup
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
    has_next_page = len(quotes) > int(page) * ITEMS_PER_PAGE,
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
    template = 'tableful.html' if TABLEFUL_MODE else 'index.html'
    return render_template(template,
                           top_ten_tags=TOP_TEN_TAGS,
                           **params)


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--host')
    parser.add_argument('--tableful', action='store_true')

    args = parser.parse_args()

    if args.tableful:
        TABLEFUL_MODE = True
    app.run(debug=args.debug, host=args.host)
