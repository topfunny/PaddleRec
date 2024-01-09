# !/usr/bin/python
# -*- coding: utf-8 -*-
# @author: huminghe
# @date: 2023/10/24
#


from flask import Flask, request
import os
import logging
from logging.handlers import TimedRotatingFileHandler

server_logs_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(server_logs_dir, exist_ok=True)
logging.root.setLevel(logging.NOTSET)
handler = TimedRotatingFileHandler(os.path.join(server_logs_dir, 'server.log'), when="MIDNIGHT",
                                   encoding='UTF-8', backupCount=10)
logging_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s')
handler.setFormatter(logging_format)
logging.root.addHandler(handler)

import inspect
import random
import string
import json
import sys
import predict
from gevent import pywsgi

app = Flask(__name__)


def response_return_template(code, message, result=None):
    if result:
        return {'status': {'code': code, 'message': message}, 'result': result}
    else:
        return {'status': {'code': code, 'message': message}}


@app.route("/topfunny/rank", methods=['POST'])
def rank():
    data = request.json
    history_list = data['history']
    candidate_list = data['candidate']
    history_country_list = data['history_country']
    candidate_country_list = data['candidate_country']

    app.logger.info(
        "history: " + str(history_list) + ",   candidate: " + str(candidate_list) + ",   history country: " + str(
            history_country_list) + ",   candidate country: " + str(candidate_country_list))

    result = predict.predict_author_result(history_list, candidate_list, history_country_list, candidate_country_list)
    result = [{'authorId': str(x[0]), 'score': str(x[1])} for x in result]

    return_value = response_return_template(200, 'OK', result)
    return json.dumps(return_value, ensure_ascii=False)


if __name__ == '__main__':
    port = int(sys.argv[1])
    app.logger.info('deploy server started.')

    server = pywsgi.WSGIServer(('0.0.0.0', port), app, log=app.logger, error_log=app.logger)
    server.serve_forever()