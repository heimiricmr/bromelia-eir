# -*- coding: utf-8 -*-
"""
    eir_app.utils
    ~~~~~~~~~~~~~

    This module implements utilities functions.
    
    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

import argparse
import re


def get_imei_sv(request):
    if request.has_avp("terminal_information_avp"):
        terminal_info_avp = request.terminal_information_avp

        if terminal_info_avp.has_avp("imei_avp"):
            imei = terminal_info_avp.imei_avp.data.decode("utf-8")
            if len(imei) != 15:
                raise
        else:
            raise
            
        if terminal_info_avp.has_avp("software_version_avp"):
            sv = terminal_info_avp.software_version_avp.data.decode("utf-8")
        else:
            raise

        return imei, sv


class CommandParser:
    def __init__(self, command):
        self.command = command
        self.operation = None

        self._process()


    def _process(self):
        create_pattern = re.findall(r"device create (\d{15}) (\d{2}) (DENIED|GREYLISTED)", self.command)
        get_pattern = re.findall(r"device get (\d{15})", self.command)
        update_pattern = re.findall(r"device update (\d{15}) (\d{2}) (DENIED|GREYLISTED)", self.command)
        delete_pattern = re.findall(r"device delete (\d{15})", self.command)

        if create_pattern:
            self.operation = "create"
            self.imei, self.sv, self.status = create_pattern[0]

        elif get_pattern:
            self.operation = "get"
            self.imei = get_pattern[0]

        elif update_pattern:
            self.operation = "update"
            self.imei, self.sv, self.status = update_pattern[0]

        elif delete_pattern:
            self.operation = "delete"
            self.imei = delete_pattern[0]
        
        else:
            raise Exception("Invalid eir_manager command")


def get_imei(arg):
    if isinstance(arg, argparse.Namespace) or isinstance(arg, CommandParser):
        try:
            return int(arg.imei)
        except AttributeError:
            return None


def get_sv(arg):
    if isinstance(arg, argparse.Namespace) or isinstance(arg, CommandParser):
        try:
            if arg.sv == "00":
                return None
            return int(arg.sv)

        except AttributeError:
            return None


def get_status(arg):
    if isinstance(arg, argparse.Namespace) or isinstance(arg, CommandParser):
        try:
            if arg.status == "DENIED":
                return True
            if arg.status == "GREYLISTED":
                return False
        except AttributeError:
            return None
