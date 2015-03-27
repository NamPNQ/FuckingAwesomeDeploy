from flask import Flask
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

from app import app

application = DispatcherMiddleware(Flask('dummy_app'), {
        app.config['APPLICATION_ROOT']: app})

# Run: gunicorn -w 1 -k eventlet -t 5 wsgi:application -b 0.0.0.0:5000

if __name__ == "__main__":
    run_simple('0.0.0.0', 5000, application, use_reloader=True, use_debugger=True)
