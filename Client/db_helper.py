import constant
from pymongo import MongoClient

def dbSetup():

    # mongo setup
    connect_string = constant.MONGO_HEADING + constant.MONGO_SERVER + ":" + constant.MONGO_PORT
    connection = MongoClient(connect_string)
    return connection.project
