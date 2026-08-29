import logging
import os
import subprocess
import sys

from cinema_follower.utils.logs import set_logger

try:
    set_logger()
except AttributeError as e:
    logging.error(e)

from cinema_follower.app import app
from cinema_follower.db import rq

CERT_PATH = os.path.join(os.path.realpath(__package__), 'data/certificates')


def main():
    url = 'https://127.0.0.1:5000/people'

    if sys.platform == 'win32':
        os.startfile(url)
    elif sys.platform == 'darwin':
        subprocess.Popen(['open', url])
    else:
        try:
            subprocess.Popen(['xdg-open', url])
        except OSError:
            print(f'Please open a browser on: {url}')
    app.run(debug=True, ssl_context=(os.path.join(CERT_PATH, 'cert.crt'), os.path.join(CERT_PATH, 'cert.key')))


def rq_worker():
    with app.app_context():
        worker = rq.make_worker()
        worker.work()


if __name__ == '__main__':
    main()
