DEBUG = False
TESTING = False

STRAVA_PUBLIC_TOKEN = None

STRAVA_API_ENDPOINTS = {
    'segments_explore': 'https://www.strava.com/api/v3/segments/explore',
    'segments_leaderboards': 'https://www.strava.com/api/v3/segments/{id}/leaderboard'
}

LOCATIONS = {
    # http://boundingbox.klokantech.com

    'ankara': '39.730421,32.518474,40.076332,33.007056',
    'istanbul': '40.811404,28.595554,41.199239,29.428805',
    'izmir': '38.290113,26.854949,38.545237,27.304485',
}