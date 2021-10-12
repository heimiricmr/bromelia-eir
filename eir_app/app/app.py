# -*- coding: utf-8 -*-
"""
    eir_app.app
    ~~~~~~~~~~~

    This module implements EIR's core function.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import logging

from bromelia import Bromelia
from bromelia.avps import *
from bromelia.constants import *
from bromelia.etsi_3gpp_s13.messages import MeIdentityCheckAnswer as ECA
from bromelia.etsi_3gpp_s13.messages import MeIdentityCheckRequest as ECR

from config import *
from constants import *
from models import get_equipment_status
from utils import get_imei_sv

app_logger = logging.getLogger("3gpp_eir")

#: Application initialization
app = Bromelia(config_file=config_file)
app.load_messages_into_application_id([ECA, ECR], DIAMETER_APPLICATION_S13_S13)

#: Creating alias
ECA = app.s13_s13.MICA

@app.route(application_id=DIAMETER_APPLICATION_S13_S13, command_code=EC_MESSAGE)
def ecr(request):
    """This function is the entrypoint to process S13/S13'Diameter 
    3GPP-ME-Identity-Check Request. It captures IMEISV from request, 
    upon availability, then it checks EIR's database in order to define 
    device status and reply it to MME.
    """

    hop_by_hop = request.header.hop_by_hop.hex()
    imsi = request.user_name_avp.data.decode("utf-8")

    try:
        imei, sv = get_imei_sv(request)
        app_logger.debug(f"[{hop_by_hop}] Got a request from device (IMEI: "\
                         f"{imei}, SV: {sv}) with the subscriber: {imsi}")
    except:
        app_logger.exception(f"[{hop_by_hop}] Unable to get device IMEI")
        return ECA(result_code=DIAMETER_MISSING_AVP)

    status = get_equipment_status(imei)

    if status == PASS_STATUS:
        app_logger.debug(f"[{hop_by_hop}] Device {imei} is WHITELISTED")
        return ECA(equipment_status=EQUIPMENT_STATUS_WHITELISTED)

    elif status == GREY_STATUS:
        app_logger.debug(f"[{hop_by_hop}] Device {imei} is GREYLISTED")
        return ECA(equipment_status=EQUIPMENT_STATUS_GREYLISTED)

    elif status == DENY_STATUS:
        app_logger.debug(f"[{hop_by_hop}] Device {imei} is BLACKLISTED")
        return ECA(equipment_status=EQUIPMENT_STATUS_BLACKLISTED)
