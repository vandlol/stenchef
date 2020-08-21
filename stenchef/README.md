# Stenchef

Currently under heavy development. Please contact me if you'd like to
contribute.

## setup dev environment

- install mongodb
- start mongodb
  `../start_mongodb.sh`
- install everython from the requirements.txt via your preferred mechanism
  (e.g. `pip install -r requirements.txt`)
- fill the database with basics
  `python manage.py migrate`
- create a superuser
  `python manage.py createsuperuser`
- start the server
  `python manage.py runserver`
