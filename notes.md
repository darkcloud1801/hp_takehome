# Backend Engineering Homework Notes
  
### Set up  
* Database: I elected to stay with sqlite, so there is no need to have any other service running.  
* Dependencies: I used pipenv/pyenv to get a virtual environment set up.
* Linting/Formatting: I elected to use ruff

### Deliverables
From withing the venv:
* Execute `python manage.py migrate` to create the tables in sql lite
* Execute `python manage.py createsuperuser` to create at least 1 user
* Execute `python manage.py runserver` to start a new server on 8000
* Execute `python manage.py test` to run tests.

