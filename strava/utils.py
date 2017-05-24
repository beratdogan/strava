import grequests
import requests
from flask import Flask


app = Flask('strava')


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
                    'total_distance': 0,
                    'total_moving_time': 0,
                    'total_elapsed_time': 0,
                    'avg_speed': entry['distance'] / entry['moving_time'],
                    'count': 0,
                }

            athletes[entry['athlete_id']]['count'] += 1
            athletes[entry['athlete_id']]['total_distance'] += entry['distance']
            athletes[entry['athlete_id']]['total_moving_time'] += entry['moving_time']
            athletes[entry['athlete_id']]['total_elapsed_time'] += entry['elapsed_time']

    return athletes


def calculate_score(athlete):
    """
    There are simple rules of calculating scores as below:
    - immovability: Riders who don't take too many breaks while riding earns
                    extra points. Since this doesn't have a big impact,
                    the coefficient is very low.
    - distance: This displays the total distance traveled within the given
                    boundaries. Passing a certain threshold earns
                    extra points. Since long distance bike riding is important,
                    the coefficient is higher.
    - avg speed: This displays the average riding speed for all the distance
                    traveled within the given boundaries. An average speed is
                    considered better. The riders who are not too slow or
                    too fast earns extra points.
    - count: This displays the number of different segments the rider have
                    traveled on within the given boundaries. This number
                    signifies how "continuous" the rider is. Because of this,
                    the parameter has a very high coefficient.
    After the values of these parameters are calculated, they are multiplied
                    with their coefficients and the total sum is calculated.
    """
    immovability = abs(athlete['total_elapsed_time'] - athlete['total_moving_time'])
    if immovability > 10:
        immovability_score = 0
    else:
        immovability_score = 10

    distance = athlete['total_distance']
    distance_cluster = divmod(distance, 50)[0]
    distance_score = distance_cluster * 10

    avg_speed = athlete['avg_speed']
    if 15 >= avg_speed >= 10:
        avg_speed_bonus = 10
    else:
        avg_speed_bonus = -10

    count = athlete['count']
    count_bonus = 0
    if count >= 7:
        count_bonus = 10
    elif count >= 3:
        count_bonus = 5

    return 1 * immovability_score + 4 * distance_score + 2 * avg_speed_bonus + 5 * count_bonus


def normalize_scores(athletes):
    sum_scores = sum(athlete['score'] for athlete_id, athlete in athletes.iteritems())

    for athlete_id, athlete in athletes.iteritems():
        athlete['score'] = athlete['score'] / sum_scores
