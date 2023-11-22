import sqlite3
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
import json
from lxml import etree
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

def init_db():
    conn = sqlite3.connect('data/requests.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (path TEXT, body TEXT, timestamp TEXT)''')
    conn.commit()
    conn.close()

class S(BaseHTTPRequestHandler):
    def _set_response(self, content_type='text/html'):
        self.send_response(200)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        self.save_to_db(self.path, post_data.decode('utf-8'))
        self._set_response()
        self.wfile.write("POST request for {}".format(self.path).encode('utf-8'))

    def do_GET(self):
        path = self.path
        records = self.retrieve_from_db(path)
        rss_feed = self.create_rss_feed(path, records)
        self._set_response('application/rss+xml')
        self.wfile.write(etree.tostring(rss_feed))

    def save_to_db(self, path, body):
        timestamp = datetime.now().isoformat()
        conn = sqlite3.connect('data/requests.db')
        c = conn.cursor()
        c.execute("INSERT INTO requests (path, body, timestamp) VALUES (?, ?, ?)",
                  (path, body, timestamp))
        conn.commit()
        conn.close()

    def retrieve_from_db(self, path):
        conn = sqlite3.connect('data/requests.db')
        c = conn.cursor()
        c.execute("SELECT body, timestamp FROM requests WHERE path = ?", (path,))
        records = c.fetchall()
        conn.close()
        return [{"body": body, "timestamp": timestamp} for body, timestamp in records]

    def create_rss_feed(self, path, records):
        rss = etree.Element('rss', version='2.0')
        channel = etree.SubElement(rss, 'channel')
        title = etree.SubElement(channel, 'title')
        title.text = f"RSS Feed for {path}"

        for record in records:
            item = etree.SubElement(channel, 'item')
            title = etree.SubElement(item, 'title')
            title.text = f"POST at {record['timestamp']}"
            pubDate = etree.SubElement(item, 'pubDate')
            pubDate.text = record['timestamp']
            description = etree.SubElement(item, 'description')
            try:
                pretty_json = json.dumps(json.loads(record['body']), indent=4)
                highlighted_json = highlight(pretty_json, JsonLexer(), HtmlFormatter(full=True, style='colorful'))
                description.text = etree.CDATA(highlighted_json)
            except:
                description.text = record['body']

        return rss

def run(server_class=HTTPServer, handler_class=S, port=8000):
    logging.basicConfig(level=logging.INFO)
    init_db()
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    run()
