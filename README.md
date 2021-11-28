# Microservice with REST API #

### Introduction ###

In order to use all the functionalities of the application, sample data should be sent
with POST /db with body {"q": "Hobbit"} from the page https://www.googleapis.com/books/v1/volumes?q=Hobbit.

### Technology stack ###

Python 3.8.10, Flask, Git

### Requirements ###

* Python3.8.10
* Unoccupied port 5000

### Prepare virtualenv (Linux) ###

* Prepare directory for virtual env (on the root of project):
	`mkdir venv`
* Prepare virtual env module:
	`sudo apt-get install python3-venv`
* Create venv:
	`python3 -m venv ./venv/`
* Checkout to venv:
	`source ./venv/bin/activate`
* Install requirements:
	`pip install -r requirements.txt`
* Check requirements:
	`pip list`

### Run application locally ###

* Source the virtaul enviroment:
	`source ./vevn/bin/activate`
* Run flask application:
	`flask run`
