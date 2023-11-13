# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""datq query test class."""
import io
from unittest.mock import MagicMock, patch

import pytest
import pytest_check as check

from msticpy.common.exceptions import (
    MsticpyConnectionError,
    MsticpyDataQueryError,
    MsticpyNotConnectedError,
    MsticpyUserConfigError,
)
from msticpy.data.drivers.netwitness_driver import NetwitnessDriver, NetwitnessAPI

from ...unit_test_lib import get_test_data_path

_TEST_DATA = get_test_data_path()

NETWITNESS_CLI_PATCH = NetwitnessDriver.__module__ + ".NetwitnessAPI"

def cli_connect(**kwargs):
    cause = MagicMock()
    cause.response.status_code="200"
    return _MockNetwitnessService()

class _MockNetwitnessService(MagicMock):
    """Netwitness service mock."""

    def __init__(self):
        """Mock method."""
        super().__init__()
    
    @property
    def login(self):
         """Mock method."""
         self.response.status_code="200"

@patch(NETWITNESS_CLI_PATCH)
def test_netwitness_connect_no_params(netwitness_api):
    """Check failure with no args."""
    netwitness_api.connect = cli_connect

    nw_driver = NetwitnessDriver()
    check.is_true(nw_driver.loaded)

    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        nw_driver.connect()
        check.is_false(nw_driver.connected)
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)

@patch(NETWITNESS_CLI_PATCH)
def test_netwitness_connect_errors(netwitness_api):
    """Check connect failure errors."""
    netwitness_api.connect = cli_connect

    netwitness_driver = NetwitnessDriver()
    check.is_true(netwitness_driver.loaded)

    print("connected", netwitness_driver.connected)
    with pytest.raises(MsticpyConnectionError) as mp_ex:
        netwitness_driver.connect(
            nwhost="nwhost", nwuser="nwusername", nwpassword="nwpassword"
        )
        print("connected", netwitness_driver.connected)
        check.is_false(netwitness_driver.connected)
    check.is_in("Netwitness connection", mp_ex.value.args)

@patch(NETWITNESS_CLI_PATCH)
def test_netwitness_query_success(netwitness_api):
    """Check loaded true."""
    netwitness_api.login = cli_connect
    netwitness_driver = NetwitnessDriver()

    # trying to get these before connecting should throw
    with pytest.raises(MsticpyNotConnectedError) as mp_ex:
        netwitness_driver.query("some query")
        check.is_false(netwitness_driver.connected)
    check.is_in("not connected to Netwitness.", mp_ex.value.args)

    netwitness_driver.connect(nwhost="localhost", nwuser="testuser", nwpassword="testpass")
    check.is_true(netwitness_driver.connected)