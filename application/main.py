from gevent import monkey; monkey.patch_all()
import env; env.setup()
import logger; logger.setup()

import logging
log = logging.getLogger()

# An example gevent/flask app
import flask
app = flask.Flask(__name__)

@app.route('/get', methods=['GET'])
def get():
    # flask.request.args for GET
    # flask.request.form for POST
    return "Hello World %s" % flask.request.args
    
if __name__ == '__main__':
    from gevent.wsgi import WSGIServer
    http_server = WSGIServer(('127.0.0.1', 5000), app)
    http_server.serve_forever()