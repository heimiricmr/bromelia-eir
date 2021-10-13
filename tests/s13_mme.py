# -*- coding: utf-8 -*-
"""
    bromelia_eir.mme
    ~~~~~~~~~~~~~~~~

    This module contains an example on how to setup a dummy MME
	by using the Bromelia class features of bromelia library.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import datetime
import time
import sys

from bromelia import Diameter
from bromelia.avps import *
from bromelia.constants import *
from bromelia.etsi_3gpp_s13.avps import *
from bromelia.etsi_3gpp_s13.messages import MeIdentityCheckAnswer as ECA
from bromelia.etsi_3gpp_s13.messages import MeIdentityCheckRequest as ECR
from bromelia.etsi_3gpp_s6a_s6d.avps import *

LOCAL_HOSTNAME = "mme.epc.mynetwork.com"
LOCAL_DOMAIN = "epc.mynetwork.com"
LOCAL_IP_ADDRESS = "127.0.0.1"
LOCAL_PORT = 3868

REMOTE_HOSTNAME = "eir.epc.mynetwork.com"
REMOTE_DOMAIN = "epc.mynetwork.com"
REMOTE_IP_ADDRESS = "127.0.0.1"
REMOTE_PORT = 3870

#: Setting up Diameter connection
config = {
            'MODE': 'CLIENT', 
            'APPLICATIONS': [{
                                'vendor_id': VENDOR_ID_3GPP, 
                                'app_id': DIAMETER_APPLICATION_Gx
            }], 
            'LOCAL_NODE_HOSTNAME': LOCAL_HOSTNAME, 
            'LOCAL_NODE_REALM': LOCAL_DOMAIN, 
            'LOCAL_NODE_IP_ADDRESS': LOCAL_IP_ADDRESS, 
            'LOCAL_NODE_PORT': LOCAL_PORT, 
            'PEER_NODE_HOSTNAME': REMOTE_HOSTNAME, 
            'PEER_NODE_REALM': REMOTE_DOMAIN, 
            'PEER_NODE_IP_ADDRESS': REMOTE_IP_ADDRESS, 
            'PEER_NODE_PORT': REMOTE_PORT, 
            'WATCHDOG_TIMEOUT': 60
}

app = Diameter(config=config)


def create_ecr(index):
    imei = 123456789000000 + index
    imsi = 999000000000000 + index

    ecr_avps = {
                 "session_id": app.config["LOCAL_NODE_HOSTNAME"],
                 "origin_host": app.config["LOCAL_NODE_HOSTNAME"],
                 "origin_realm": app.config["LOCAL_NODE_REALM"],
                 "destination_realm": app.config["PEER_NODE_REALM"],
                 "destination_host": app.config["PEER_NODE_HOSTNAME"],
                 "user_name": str(imsi),
                 "terminal_information": [
                                            ImeiAVP(str(imei)),
                                            SoftwareVersionAVP("12")
                 ]
    }
    return ECR(**ecr_avps)


def performance(total_num_msgs, num_transactions, time_frame):
    ecrs = list()
    total_recvd = 0

    previous = app._association.num_answers
    start = datetime.datetime.utcnow()

    print("\n")
    for index in range(1, total_num_msgs + 1):
        ecr = create_ecr(index)
        ecrs.append(ecr)

        if index % num_transactions == 0:
            print(f"sent: {index}, recvd: {total_recvd}, pending: {index - total_recvd} ({100*round(total_recvd/index,2)}%)")
            app.send_messages(ecrs)
            ecrs = list()

            time.sleep(time_frame)

            total_recvd = app._association.num_answers - previous

    app.send_messages(ecrs)

    expiration_timer = 10
    while total_recvd < total_num_msgs:
        if expiration_timer == 0:
            raise

        print(f"index: {total_num_msgs}, total_recv: {total_recvd}, pending: {total_num_msgs - total_recvd} ({100*round(total_recvd/(total_num_msgs),2)}%)")
        total_recvd = app._association.num_answers - previous

        time.sleep(1)
        expiration_timer -= 1


    stop = datetime.datetime.utcnow()

    executed_time = (stop - start).seconds
    try:
        _tps = round(total_num_msgs/executed_time,3)
    except ZeroDivisionError:
        _tps = None

    print(f"\nexecution time: {executed_time} seconds")
    print(f"tps: {_tps} msgs/seconds")
    

def execute():
    try:
        print(f"\n===================================================\n")

        number_of_msgs = int(input(">> Total number of messages: "))
        msgs_per_cycle = int(input(">> Number of messages per cycle: "))
        time_frame = float(input(">> Cycle extension (in seconds): "))
        performance(number_of_msgs, msgs_per_cycle, time_frame)

        print(f"\n===================================================\n")
    except:
        sys.exit(0)


if __name__ == "__main__":
    with app.context():

        while app.is_open():
            execute()

            while 1:
                _continue = input("\n>> Continue with more performance testing? (Y/N) ")
                if not (_continue == "Y" or _continue == "y"):
                    break
                execute()

            break
