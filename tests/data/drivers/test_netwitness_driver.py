# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
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

from msticpy.data.drivers.netwitness_driver import NetwitnessDriver, NetwitnessAPI

from ...unit_test_lib import get_test_data_path

_TEST_DATA = get_test_data_path()

NETWITNESS_CONNECT_PATCH = NetwitnessDriver.__module__ + ".NetwitnessAPI"

def cli_connect(**kwargs):
    """Return None if magic isn't == kql."""
    cause = MagicMock()
    cause.body = bytes("Test body stuff", encoding="utf-8")
    cause.status = 404
    cause.reason = "Page not found."
    cause.headers = "One Two Three"
    if kwargs.get("host") == "AuthError":
        raise sp_client.AuthenticationError(cause=cause, message="test AuthHeader")
    if kwargs.get("host") == "HTTPError":
        cause.body = io.BytesIO(cause.body)
        raise sp_client.HTTPError(response=cause, _message="test HTTPError")
    return _MockNetwitnessService()

class _MockSplunkService(MagicMock):
    """Splunk service mock."""

    def __init__(self):
        """Mock method."""
        super().__init__()
        self.searches = [
            _MockSplunkSearch("query1", "get stuff from somewhere"),
            _MockSplunkSearch("query2", "get stuff from somewhere"),
        ]
        self.jobs = MagicMock()
        self.jobs = _MockSplunkCall

    @property
    def saved_searches(self):
        """Mock method."""
        return self.searches

    @property
    def fired_alerts(self):
        """Mock method."""
        return [
            _MockAlert("alert1", 10),
            _MockAlert("alert2", 10),
            _MockAlert("alert3", 10),
            _MockAlert("alert4", 10),
        ]

    @staticmethod
    def _query_response(query, **kwargs):
        del kwargs
        return query

@patch(NETWITNESS_CONNECT_PATCH)
def test_netwitness_connect_no_params(NetwitnessAPI):
    """Check failure with no args."""
    netwitness_client.connect = cli_connect

# @patch(NETWITNESS_CONNECT_PATCH)
# def test_netwitness_connect_req_params(NetwitnessAPI):
#     """Check load/connect success with required params."""

# @patch(NETWITNESS_CONNECT_PATCH)
# def test_netwitness_connect_errors(NetwitnessAPI):
#     """Check connect failure errors."""

# @patch(NETWITNESS_CONNECT_PATCH)
# def test_netwitness_fired_alerts(NetwitnessAPI):
#     """Check fired alerts."""

# @patch(NETWITNESS_CONNECT_PATCH)
# def test_netwitness_saved_searches(NetwitnessAPI):
#     """Check saved searches."""