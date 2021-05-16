import logging
import os
from typing import Text
from peewee import *
from discord.enums import ExpireBehavior
from peewee import AutoField, ForeignKeyField, Model, IntegerField, PrimaryKeyField, TextField, SqliteDatabase, DoesNotExist, DateTimeField, UUIDField, IntegrityError
from playhouse.shortcuts import model_to_dict, dict_to_model  # these can be used to convert an item to or from json http://docs.peewee-orm.com/en/latest/peewee/playhouse.html#model_to_dict
from playhouse.sqlite_ext import RowIDField
from datetime import datetime
from peewee import MySQLDatabase
from playhouse.shortcuts import ReconnectMixin
from flask import Flask

db = MySQLDatabase("SchoolSimplified", user="portaladmin", password="portalturtle",host="3.142.255.184", port=3306)
logger = logging.getLogger(__name__) 

def iter_table(model_dict):
    """Iterates through a dictionary of tables, confirming they exist and creating them if necessary."""
    for key in model_dict:
        if not db.table_exists(key):
            db.connect(reuse_if_open=True)
            db.create_tables([model_dict[key]])
            logger.debug(f"Created table '{key}'")
            db.close()

class BaseModel(Model):
    """Base Model class used for creating new tables."""
    class Meta:
        database = db


class VCChannelInfo(BaseModel):
    id = AutoField()
    ChannelID = TextField()
    name = TextField()
    authorID = TextField()
    datetimeObj = DateTimeField(default = datetime.now())
    used = BooleanField()

class NameAva(BaseModel):
    id = AutoField()
    name = TextField()
    free = BooleanField()

class IgnoreThis(BaseModel):
    id = AutoField()
    channelID = TextField()
    authorID = BooleanField()

app = Flask(__name__)

# This hook ensures that a connection is opened to handle any queries
# generated by the request.
@app.before_request
def _db_connect():
    db.connect()

# This hook ensures that the connection is closed when we've finished
# processing the request.
@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        db.close()

tables = {"VoiceChannelInfo" : VCChannelInfo, "IgnoreThis": IgnoreThis}
iter_table(tables)