# -*- coding: utf-8 -*-
"""
    eir_app.models
    ~~~~~~~~~~~~~~

    This module contains EIR's database models.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import logging

from config import *
from constants import *

from sqlalchemy import create_engine
from sqlalchemy import BigInteger, Column, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

models_logging = logging.getLogger("eir_manager.models")

engine = create_engine(database_uri, echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class Device(Base):
    __tablename__ = "devices"
    id = Column(BigInteger, primary_key=True)
    imei = Column(BigInteger)
    sv = Column(Integer)
    is_denied = Column(Boolean)

    def __repr__(self):
        if self.is_denied:
            return f"({self.imei}, DENIED)"
        return f"({self.imei}, GREYLISTED)"


Base.metadata.create_all(engine)


def get_equipment_status(imei):
    """This function implements the query into EIR's database in order 
    to fetch the device status. If device exists in database, then an 
    administration procedure has been executed. It may be assigned as 
    a denied and greylisted device. Otherwise, if device does not exist
    in database, it is allowed to register in the network"""

    try:
        device = session.query(Device).filter(Device.imei==imei).one_or_none()
        session.close()
    except Exception as e:
        models_logging.exception(f"An error has happened: {e.args[0]}")
        session.rollback()
        session.close()
        return 

    if device is None:
        models_logging.info(f"({imei},PASS_STATUS)")
        return PASS_STATUS

    if device.is_denied:
        models_logging.info(f"({imei},DENY_STATUS)")
        return DENY_STATUS

    models_logging.info(f"({imei},GREY_STATUS)")
    return GREY_STATUS
