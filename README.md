# Stenchef

Currently under heavy development. Please contact me if you'd like to
contribute.


## setup dev environment

- clone this repo
  `git clone https://github.com/vandlol/stenchef`
- install mongodb, npm, redis
  `apt install mongodb npm redis`
  (or whatever is the command to install software via your package manager)
- start mongodb and redis
  `systemctl start mongodb.service`
  `systemctl start redis.service`
- switch inside the repo folder
  `cd stenchef`
- install everything from the requirements.txt via your preferred mechanism
  (e.g. `pip3 install -r requirements.txt`)
- switch to the project directory within the repo folder
  `cd stenchef`
- fill the database with basics
  `python manage.py migrate`
- import defaults into the Database
  `python manage.py loaddata ../fixtures/fixture_defaults.json`
- start the server
  `python manage.py runserver`
- initiate and build css (tailwind)
  `python manage.py tailwind install`
  `python manage.py tailwind build`
- (optional) watch for css changes - background process
  `python manage.py tailwind start &`

## add npm/tailwind modules

- go to `stenchef/stenchef/warehouse/static_src`; run npm there
