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

from ...unit_test_lib import get_test_data_path

NETWITNESS_CLI_PATCH = NetwitnessDriver.__module__

def cli_connect(**kwargs):
    cause = MagicMock()
    cause.body = bytes("Test body stuff", encoding="utf-8")
    cause.status = 404
    cause.reason = "Page not found."
    cause.headers = "One Two Three"
    if kwargs.get("host") == "AuthError":
        raise host.AuthenticationError(cause=cause, message="test AuthHeader")
    if kwargs.get("host") == "HTTPError":
        cause.body = io.BytesIO(cause.body)
        raise host.HTTPError(response=cause, _message="test HTTPError")
    return _MockNetwitnessService()

class _MockNetwitnessCall:
    def create(query, **kwargs):
        del kwargs
        return _MockAsyncResponse(query)

class _MockAsyncResponse:
    stats = {
        "isDone": "0",
        "doneProgress": 0.0,
        "scanCount": 1,
        "eventCount": 100,
        "resultCount": 100,
    }

class _MockNetwitnessService(MagicMock):
    """Netwitness service mock."""
    def __init__(self):
        """Mock method."""
        super().__init__()
        self.searches = [
            _MockSplunkSearch("query1", "get stuff from somewhere"),
            _MockSplunkSearch("query2", "get stuff from somewhere"),
        ]
        self.jobs = MagicMock()
        self.jobs = _MockNetwitnessCall

@patch(NETWITNESS_CLI_PATCH)
def test_netwitness_connect_no_params(netwitness_client):
    """Check failure with no args."""
    netwitness_client.connect = cli_connect

    nw_driver = NetwitnessDriver()
    check.is_true(nw_driver.loaded)

    with pytest.raises(MsticpyUserConfigError) as mp_ex:
        nw_driver.connect()
        check.is_false(nw_driver.connected)
    check.is_in("no Netwitness connection parameters", mp_ex.value.args)