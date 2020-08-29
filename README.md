# Stenchef

Currently under heavy development. Please contact me if you'd like to
contribute.

Moved Fixtures to https://github.com/vandlol/stenchef_fixtures to kepp this repo a bit lower footprint.

## setup dev environment

- install mongodb
- start mongodb
  `../start_mongodb.sh`
- install everything from the requirements.txt via your preferred mechanism
  (e.g. `pip install -r requirements.txt`)
- fill the database with basics
  `python manage.py migrate`
- create a superuser
  `python manage.py createsuperuser`
- start the server
  `python manage.py runserver`
