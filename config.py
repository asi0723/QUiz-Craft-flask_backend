import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "postgresql://dylan:riAov0tfECBcpraEmiKFawR72c0zWzI4@dpg-cll2q2cjtl8s73f6di0g-a.oregon-postgres.render.com/quiz_craft"