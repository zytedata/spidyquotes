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

# PLAN:
# [X] browse by tags
# [X] add top ten tags
# [X] add pagination
# [ ] add alternate template with data in JS code
# [ ] add alternate template with AJAX UI
# [ ] add microdata markup
# [ ] add alternate template with tables layout


def top_ten_tags():
    tags = (tag for d in QUOTES for tag in d['tags'])
    return Counter(tags).most_common(10)


TOP_TEN_TAGS = top_ten_tags()


@app.route("/")
def index():
    return render_template('index.html',
                           quotes=QUOTES[0:10],
                           top_ten_tags=TOP_TEN_TAGS)


@app.route("/tag/<tag>/")
@app.route("/tag/<tag>/page/<page>/")
def quotes_by_tag(tag, page=1):
    quotes = [q for q in QUOTES if tag in q['tags']]
    start, end = (int(page) - 1) * 10, int(page) * 10
    return render_template('index.html',
                           quotes=quotes[start:end],
                           page=int(page),
                           has_next=len(quotes) > int(page) * 10,
                           tag=tag,
                           top_ten_tags=TOP_TEN_TAGS)


if '__main__' == __name__:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--host')

    args = parser.parse_args()
    app.run(debug=args.debug, host=args.host)
