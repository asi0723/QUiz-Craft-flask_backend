# QUiz-Craft-flask_backend

## Overview

This is a backend RESTAPI Built with Flask and used sqlAlchemy as the ORM. The database is hosted using vercel serverless postgress db

## Installation
Clone my git Repo
```
git clone {my repo} .
```
Set Up python virtual environments
```
python -m venv venv
```
Activating the virtual env
```
venv\Scripts\activate
```
Installing Requirements for the project
```
pip install -r requirements.txt
```
Create the db in flask shell and do migrations
```
  flask db init
  flask db migrate -m "initial migration"
  flask db upgrade
```
Initializing THe db if you are using a different URI other than my hosted one on vercel
```
  flask shell
  db.create_all()
```
ANd Finally run the code
```
python run.py
```
