# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest.mock import MagicMock, patch
import pytest
import pytest_check as check
from msticpy.data.drivers.netwitness_driver import NetwitnessDriver, NetwitnessAPI
from msticpy.common.exceptions import (
    MsticpyNotConnectedError,
    MsticpyUserConfigError,
)

def test_netwitness_connect_no_params():
    netwitness=NetwitnessDriver()
    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        netwitness.connect() ## No arguments provided
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)

def test_netwitness_connect_req_params():
    netwitness=NetwitnessDriver()
    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        netwitness.connect(nwhost="1.1.1.1") ## Missing parameters provided
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)

@patch('msticpy.data.drivers.netwitness_driver.NetwitnessAPI')
def test_netwitness_connection_success(mock_netwitness_api):
    netwitness=NetwitnessDriver()
    mock_netwitness_api.return_value=MagicMock(status_code="200")
    netwitness.connect(nwhost="1.1.1.1",nwuser="username",nwpassword="pass")
    check.is_true(netwitness.connected)


#def test_netwitness_connect_no_params -- Done
#def test_netwitness_connect_req_params -- Done
#def test_netwitness_query_success