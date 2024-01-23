from flask import Flask
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base, declared_attr
Base = declarative_base()


flask_app = Flask(__name__)
flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:qwerty@localhost:5432/furnace_db'
flask_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
# app has been set and configured


Base = declarative_base()

e = create_engine("postgresql://postgres:qwerty@localhost:5432/furnace_db", echo=False)



# session_ = Session(e)
