#!/bin/bash
if [[ ! -d "venv" ]]; then
    echo Creating virtualenv...
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt

export FLASK_APP=app/app.py

if [[ ! -d "migrations" ]]; then
    echo INIT THE migrations folder
    flask db init
fi

flask db migrate
flask db upgrade
flask run