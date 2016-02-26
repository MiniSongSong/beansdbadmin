# coding: utf-8
from flask import Flask
from flask import render_template as tmpl

from beansdbadmin.tools.gc import GCRecord, SQLITE_DB_PATH, update_gc_status
from beansdbadmin.models.server import (
    get_all_server_stats, get_all_buckets_key_counts, get_all_buckets_stats
)
from beansdbadmin.models.proxy import Proxies


app = Flask(__name__)


@app.route('/')
@app.route('/index/')
def index():
    return tmpl('index.html')


@app.route('/gc/')
def gc():
    gc_record = GCRecord(SQLITE_DB_PATH)
    update_gc_status(gc_record)
    records = gc_record.get_all()
    return tmpl('gc.html', gc_records=sorted(records, reverse=True))


@app.route('/servers/')
def servers():
    server_infos = get_all_server_stats()
    ss = [s.summary_server() for s in server_infos]
    return tmpl('servers.html', servers=ss)


@app.route('/buckets/')
def buckets():
    server_buckets = get_all_buckets_stats(1)
    return tmpl('buckets.html', server_buckets=server_buckets)


@app.route('/sync/')
def sync():
    bs = get_all_buckets_key_counts(16)
    return tmpl('sync.html', buckets=bs)


@app.route('/proxies/')
def db_proxys():
    proxies = Proxies()
    stats = proxies.get_stats()
    scores_summary = proxies.get_scores_summary()
    return tmpl('proxies.html', stats=stats, scores=scores_summary)


@app.route('/score/<server>/')
def server_scores(server):
    proxies = Proxies()
    proxy_list = sorted(proxies.proxies, key=lambda x: x.host)
    scores = proxies.get_scores(server)
    return tmpl('scores.html', server=server, proxy_list=proxy_list, scores=scores)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p", "--port", type=int, default=5000,
        help="beansdbadmin agent port number."
    )
    args = parser.parse_args()
    app.run(debug=True, host="0.0.0.0", port=args.port)


if __name__ == '__main__':
    main()
