#!/usr/bin/env python3
"""
This module empasses various functions used to query the database
"""

import os
import datetime
import logging
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.model.orm import base, Trend

log = logging.getLogger(__name__)


def get_db_session(conf):
    """Get db session"""
    engine = create_engine("mysql://%s:%s@%s/%s" % (os.environ.get("DATABASE_USERNAME"),
                                                    os.environ.get("DATABASE_PASSWORD"),
                                                    os.environ.get("DATABASE_HOST"),
                                                    os.environ.get("DATABASE_NAME")))
    base.metadata.create_all(engine)
    return scoped_session(sessionmaker())(bind=engine)


def update_stats(session, keywordId, rank, engine):
    session.add(Trend(id=uuid4(), keyword=keywordId, position=rank, engine=engine, date=datetime.date.today()))
    session.commit()
