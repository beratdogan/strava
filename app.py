import grequests
import requests
from flask import Flask
from flask import jsonify

app = Flask(__name__)


def get_segments(location):
    bounds = app.config['LOCATIONS'].get(location)
    if not bounds:
        return False

    params = {
        'access_token': app.config['STRAVA_PUBLIC_TOKEN'],
        'bounds': bounds
    }

    response = requests.get(app.config['STRAVA_API_ENDPOINTS']['segments_explore'], params=params)
    if not response.ok:
        return False

    return [segment['id'] for segment in response.json().get('segments', [])]


def get_leaderboards(segment_ids):
    params = {
        'access_token': app.config['STRAVA_PUBLIC_TOKEN'],
        'per_page': 50
    }

    url = app.config['STRAVA_API_ENDPOINTS']['segments_leaderboards']
    urls = [url.format(id=segment_id) for segment_id in segment_ids]
    reqs = [grequests.get(url, params=params) for url in urls]

    for resp in grequests.imap(reqs):
        if not resp.ok:
            continue
        yield resp.json()


def get_leaders(location):
    segments = get_segments(location)
    leaderboards = get_leaderboards(segments)

    athletes = {}
    for leaderboard in leaderboards:
        for entry in leaderboard['entries']:
            if entry['athlete_id'] not in athletes:
                athletes[entry['athlete_id']] = {
                    'athlete_name': entry['athlete_name'],
                    'athlete_gender': entry['athlete_gender'],
                    'distance': entry['distance'],
                    'moving_time': entry['moving_time'],
                    'elapsed_time': entry['elapsed_time'],
                    'avg_speed': entry['distance'] / entry['moving_time'],
                    'count': 0,
                }
            athletes[entry['athlete_id']]['count'] += 1

    return {k: v for k, v in athletes.iteritems() if v['count'] > 1}


@app.route('/', defaults={'location': 'istanbul'})
@app.route('/<string:location>')
def active_atheletes(location):
    leaders = get_leaders(location.lower())

    return jsonify(leaders)


if __name__ == '__main__':
    app.config.from_object('strava.settings_default')
    app.config.from_object('strava.settings_local')
    app.run()
