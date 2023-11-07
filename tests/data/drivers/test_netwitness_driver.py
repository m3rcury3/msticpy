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
        netwitness.connect() ## No arguments provided
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)

def test_netwitness_connect_req_params():
    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        netwitness=NetwitnessDriver()
        netwitness.connect(nwhost="1.1.1.1") ## Missing parameters provided
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)


#def test_netwitness_connect_no_params -- Done
#def test_netwitness_connect_req_params
#def test_netwitness_connect_errors
#def test_netwitness_fired_alerts
#def test_netwitness_saved_searches
#def test_netwitness_query_success