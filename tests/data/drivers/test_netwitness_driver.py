# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""datq query test class."""
import io
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
import pytest_check as check

from msticpy.common.exceptions import (
    MsticpyConnectionError,
    MsticpyDataQueryError,
    MsticpyNotConnectedError,
    MsticpyUserConfigError,
)
from msticpy.data.drivers.netwitness_driver import NetwitnessDriver

_FAKE_STRING="123456789"

def cli_connect(**kwargs):
    mock=MagicMock()
    mock.status="200"

@patch(NetwitnessDriver.__module__)
def test_netwitness_connect_no_params(netwitness_client):
    """Check failure with no args."""
    netwitness_client.connect = cli_connect

    nw_driver = NetwitnessDriver()
    check.is_true(nw_driver.loaded)

    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        nw_driver.connect()
        check.is_false(nw_driver.connected)
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)

@patch(NetwitnessDriver.__module__)
def test_netwitness_connect_req_params(netwitness_client):
    """Check load/connect success with required params."""
    netwitness_client.connect = cli_connect

    nw_driver = NetwitnessDriver()
    check.is_true(nw_driver.loaded)

    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        nw_driver.connect(nwhost="netwitnesshost", nwport="50103", nwuser="testuser", nwpassword=_FAKE_STRING)  # nosec
        check.is_true(nw_driver.connected)
    check.is_in("missing Netwitness required parameters", mp_ex.value.args)