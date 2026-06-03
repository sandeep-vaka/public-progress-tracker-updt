from mongoengine import connect
from config.settings import Config

def init_db():
    connect(host=Config.MONGO_URI)
