# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import pytest_check as check
from msticpy.data.drivers.netwitness_driver import NetwitnessDriver
from msticpy.common.exceptions import (
    MsticpyUserConfigError,
    MsticpyConnectionError,
)

def test_netwitness_connect_no_params():
    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        netwitness=NetwitnessDriver()
        netwitness.connect() ## No arguments supplied by user
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)

def test_netwitness_connect_errors():
    with pytest.raises(MsticpyConnectionError) as mp_ex:
        netwitness=NetwitnessDriver()
        netwitness.connect(nwhost="nwhostname",nwuser="nwusername",nwpassword="nwpass")
    check.is_in("Netwitness connection", mp_ex.value.args)

# def test_netwitness_connect_success():

# def test_netwitness_query_success():