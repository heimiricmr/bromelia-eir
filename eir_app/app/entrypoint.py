# -*- coding: utf-8 -*-
"""
    eir_app.entrypoint
    ~~~~~~~~~~~~~~~~~~

    The central entrypoint to run EIR network function.

    :copyright: (c) 2021-present Henrique Marques Ribeiro.
    :license: MIT, see LICENSE for more details.
"""

from app import app

if __name__ == "__main__":
    app.run()   #: It will be blocked until connection has been established