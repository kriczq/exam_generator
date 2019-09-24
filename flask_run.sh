#!/bin/bash
source venv/bin/activate

export FLASK_APP=app/app.py

if [[ ! -d "migrations" ]]; then
    echo INIT THE migrations folder
    flask db init
fi

flask db migrate
flask db upgrade
flask run