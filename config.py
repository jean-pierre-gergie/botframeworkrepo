#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "073c1420-93a8-4480-a8c9-4cafa3cd3d16")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "Mx38Q~J8MFL5pdzDQ~wRae0m.zcotdFA5SF7ZcCv")

