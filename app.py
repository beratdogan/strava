from flask import jsonify

from strava.utils import app, get_leaders, calculate_score, normalize_scores


@app.route('/', defaults={'location': 'istanbul'})
@app.route('/<string:location>')
def active_athletes(location):
    athletes = get_leaders(location.lower())

    filtered_athletes = {k: v for k, v in athletes.iteritems() if v['count'] > 1}

    return jsonify(filtered_athletes)


@app.route('/highscores', defaults={'location': 'istanbul'})
@app.route('/highscores/<string:location>')
def high_scores(location):
    athletes = get_leaders(location.lower())

    for athlete_id, athlete in athletes.iteritems():
        athlete['score'] = calculate_score(athlete)

    normalize_scores(athletes)

    return jsonify(athletes)


if __name__ == '__main__':
    app.config.from_object('strava.settings_default')
    app.config.from_object('strava.settings_local')
    app.run()
