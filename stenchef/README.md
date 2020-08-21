# Stenchef

Currently under heavy development. Please contact me if you'd like to
contribute.

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
optional step: - import fixtures (takes a long time)
 `python manage.py loaddata meta/setup/*.json catalog/setup/*.json`
