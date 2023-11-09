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
    cause.body = bytes("Test body stuff", encoding="utf-8")
    cause.status_code = 200
    cause.reason = "Page not found."
    cause.headers = "One Two Three"
    if kwargs.get("host") == "AuthError":
        raise netwitness_api.AuthenticationError(cause=cause, message="test AuthHeader")
    if kwargs.get("host") == "HTTPError":
        cause.body = io.BytesIO(cause.body)
        raise netwitness_api.HTTPError(response=cause, _message="test HTTPError")
    return _MockSplunkService()

class _MockSplunkService(MagicMock):
    """Netwitness service mock."""

    def __init__(self):
        """Mock method."""
        super().__init__()

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
def test_netwitness_connect_req_params(netwitness_api):
    """Check load/connect success with required params."""
    netwitness_api.connect = cli_connect

    netwitness_driver = NetwitnessDriver()
    check.is_true(netwitness_driver.loaded)

    netwitness_driver.connect(nwhost="localhost", nwuser="ian", nwpassword="123456")
    check.is_true(netwitness_driver.connected)