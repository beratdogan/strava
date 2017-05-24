# Strava
Strava (strava.com) is an online social platform for cyclers to record their rides and compare them with other users.
This basic project allows to compare riders in given bounds by how many times they ride in different segments or calculate a fair score algorithm for them.

### Requirements
* [Flask] - micro framework
* [requests] - http client for humans
* [grequests] - using requests with gevent to boost performance

### Installation
- Install requirements:
```sh
$ pip install -r requirements.txt
```
- Define `STRAVA_PUBLIC_TOKEN` variable in _strava/settings_local.py_. You may want to use my test token: `83d66bc2fc96014efabaae851d7871d03d321468`
- Run the app
```sh
$ python app.py
```