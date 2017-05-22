from flask import Flask

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.config.from_object('strava.settings_default')
    app.config.from_object('strava.settings_local')
    app.run()