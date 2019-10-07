# Exam generator
Aplikacja pozwala na dodawanie do bazy pytań, a następnie na podstawie dodanych pytań generowanie testów o zadanych parametrach

## Wymagania
Aplikacja do działania wymaga zainstalowanego środowiska Python w wersji minimum 3.7

## Jak uruchomić aplikację
Aby uruchomić aplikację po raz pierwszy wpisz w terminalu poniższe komendy, które stworzą wirtualne środowisko oraz bazę danych:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=app/app.py

flask db init
flask db migrate
flask db upgrade
flask run
```

aplikacja będzie dostępna pod adresem:
[http://127.0.0.1:5000/](http://127.0.0.1:5000/)

Aby uruchomić aplikację po raz kolejny:
```
source venv/bin/activate
export FLASK_APP=app/app.py
flask run
```