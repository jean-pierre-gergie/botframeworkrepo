#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
    # APP_ID = os.environ.get("MicrosoftAppId", "ecc2ea47-6670-41f2-8e51-7afbaaaf4114")
    # APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "1m-8Q~znPbrn_SVSuHG6uhxJPQ8CaSUocGLaMb5Z")
