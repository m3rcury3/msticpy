# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
"""Data driver base class."""
import logging
from datetime import datetime, timedelta
from time import sleep
import asyncio
import sys
import subprocess
from requests.structures import CaseInsensitiveDict
import json
from IPython.display import JSON
import pandas as pd
from tqdm import tqdm
import requests
from typing import Any, Dict, Iterable, Optional, Set, Tuple, Union
from ..._version import VERSION
from ...common.exceptions import (
    MsticpyConnectionError,
    MsticpyDataQueryError,
    MsticpyImportExtraError,
    MsticpyUserConfigError,
)
from ...common.utility import check_kwargs, export
from ..core.query_defns import Formatters
from .driver_base import DriverBase, DriverProps, QuerySource
from ...common.pkg_config import get_http_timeout
from ...common.provider_settings import ProviderSettings, get_provider_settings
from ..core.query_defns import DataEnvironment


__version__ = 0.1
__author__ = "m3rcury3"

NETWITNESS_CONNECT_ARGS = {
    "nwhost": "(string) The Hostname or IP Address of the Netwitness service to query.",
    "nwport": "(string) The port number (the default is '50103' for a broker service).",
    "nwuser": "(string) The Netwitness account username, which is used to " + "authenticate with the Netwitness service.",
    "nwpassword": "(string) The password for the Netwitness account.",
    "nwquery_type": "The type of data to search (Metadata or Raw Logs - Default is metadata)"
}

@export
class NetwitnessDriver(DriverBase):
    """Driver to connect and query from Netwitness."""

    _NETWITNESS_REQD_ARGS = ["nwhost", "nwuser", "nwpassword"]
    _CONNECT_DEFAULTS: Dict[str, Any] = {"nwport": "50103", "nwquery_type": "metadata"}
    _TIME_FORMAT = '"%Y-%m-%d %H:%M:%S.%6N"'

    def __init__(self, **kwargs):
        """Instantiate Netwitness Driver."""
        super().__init__(**kwargs)
        self.service = None
        self._loaded = True
        self._connected = False
        if kwargs.get("debug", False):
            logger.setLevel(logging.DEBUG)
        self._required_params = self._NETWITNESS_REQD_ARGS

        self.nw_client=NetwitnessAPI(**kwargs)
    def connect(self, connection_str: Optional[str] = None, **kwargs):
        """
        Connect to Netwitness REST API.

        Parameters
        ----------
        connection_str : Optional[str], optional
            Connection string to Netwitness

        Other Parameters
        ----------------
        kwargs :
            Connection parameters can be supplied as keyword parameters.

        Notes -- ####TO DO: msticpyconfig.yaml SECTION FOR NETWITNESS####
        -----
        Default configuration is read from the DataProviders/Netwitness
        section of msticpyconfig.yaml, if available.
        """
        cs_dict = self._get_connect_args(connection_str, **kwargs)
        
        arg_dict = {
            key: val for key, val in cs_dict.items() if key in NETWITNESS_CONNECT_ARGS
        }
        nwurl="http://" + arg_dict['nwhost'] + ":" + str(arg_dict['nwport'])
        print("Connecting to " + nwurl + " as " + arg_dict['nwuser'] + "...")
        self.nw_client.login(url=nwurl, username=arg_dict['nwuser'], password=arg_dict['nwpassword'])
        print("self.nw_client.response.status_code = " + str(self.nw_client.response.status_code))
        print("self.nw_client.response.headers = " + str(self.nw_client.response.headers))
        print("self.nw_client.response.reason = " + str(self.nw_client.response.reason))
        print("Got Response: " + str(self.nw_client.response.content))
        if str(self.nw_client.response.status_code) == "200":
            raise MsticpyConnectionError(
                f"Connection error connecting to Netwitness",
                title="Netwitness connection",
                help_uri="https://msticpy.readthedocs.io/en/latest/DataProviders.html",)
        else:
            self._connected = True
            print("Connected.")

    def _get_connect_args(
        self, connection_str: Optional[str], **kwargs
    ) -> Dict[str, Any]:
        """Check and consolidate connection parameters."""
        cs_dict: Dict[str, Any] = self._CONNECT_DEFAULTS
        # Fetch any config settings
        cs_dict.update(self._get_config_settings("Netwitness"))
        # If a connection string - parse this and add to config
        if connection_str:
            cs_items = connection_str.split(";")
            cs_dict.update(
                {
                    cs_item.split("=")[0].strip(): cs_item.split("=")[1]
                    for cs_item in cs_items
                }
            )
        elif kwargs:
            # if connection args supplied as kwargs
            cs_dict.update(kwargs)
            check_kwargs(cs_dict, list(NETWITNESS_CONNECT_ARGS.keys()))

        cs_dict["nwport"] = int(cs_dict["nwport"])
        verify_opt = cs_dict.get("verify")
        if isinstance(verify_opt, str):
            cs_dict["verify"] = "true" in verify_opt.casefold()
        elif isinstance(verify_opt, bool):
            cs_dict["verify"] = verify_opt

        missing_args = set(self._required_params) - cs_dict.keys()
        if missing_args:
            raise MsticpyUserConfigError(
                "One or more connection parameters missing for Netwitness connector",
                ", ".join(missing_args),
                f"Required parameters are {', '.join(self._required_params)}",
                "All parameters:",
                *[f"{arg}: {desc}" for arg, desc in NETWITNESS_CONNECT_ARGS.items()],
                title="no Netwitness connection parameters",
            )
        return cs_dict

    def query(
        self, query: str, query_source: Optional[QuerySource] = None, **kwargs
    ) -> Union[pd.DataFrame, Any]:
        """
        Execute netwitness query and retrieve results.

        Parameters
        ----------
        query : str
            Netwitness query to execute
        query_source : QuerySource
            The query definition object

        Other Parameters
        ----------------

        Returns
        -------
        Union[pd.DataFrame, Any]
            Query results in a dataframe.
            or query response if an error.

        """
        del query_source
        if not self._connected:
            raise self._create_not_connected_err("Netwitness")
        
        nw_query_type="meta"
        query_string = query
        sessions=None
        limit=None
        flags=None
        where=None
        print("Query Type: " + nw_query_type)
        print('Executing query: ' + query + "...")
        nwqueryoutput=self.nw_client.nwquery(nw_query_type,query,**kwargs)
        return nwqueryoutput

    def query_with_results(self, query: str, **kwargs) -> Tuple[pd.DataFrame, Any]:
        """
        Execute query string and return DataFrame of results.

        Parameters
        ----------
        query : str
            Query to execute against netwitness instance.

        Returns
        -------
        Union[pd.DataFrame,Any]
            A DataFrame (if successful) or
            the underlying provider result if an error occurs.

        """
        raise NotImplementedError(f"Not supported for {self.__class__.__name__}")

class NetwitnessAPI():
    def __init__(self,**kwargs):
        self._session_data = {}
        self.session = requests.Session()
        self.session.headers = CaseInsensitiveDict()
        self.session.headers["Accept"] = "application/json"

    def login(self,url,username,password):
        self.url = url
        self.session.auth = (username,password)
        self.response = self.session.get(url=self.url,verify=False)

    def nwquery(self,nw_query_type,query_string,sessions=None, limit=None, flags=None,where=None, **kwargs):        
        if (nw_query_type=="meta"):
            payload = {'msg':'query','query': query_string}
            response = self.session.get(self.url+"/sdk",params=payload)
            _json_data = json.loads(response.content.decode("utf-8"))
            df = pd.DataFrame.from_dict(_json_data)
            final_list =[] 
            if(len(_json_data) == 3):
                raise Exception("Query Returned Empty Results")
            for x in _json_data:
                final_list += x["results"]["fields"]
            len(final_list)
            df2 = pd.json_normalize(final_list)
            #Added the following as pivot was causing a valueerror due to duplicate values occurring when 'pivoting'
            df3=df2[["group","type","value"]].drop_duplicates(subset=["group","type"]).pivot(index="group",columns=["type"])
            columns = [x[1] for x in list(df3.columns)]
            df3.columns = columns
            df3["time"] = pd.to_datetime(df3["time"], unit="s")
            return df3

        elif (nw_query_type == "raw"):
            response = self.session.get(self.url+"/sdk/packets",params=query_string)
            return response
            #print(response.content.decode())
        elif(nw_query_type == "msearch"):
            #/sdk?msg=msearch&force-content-type=text/plain&search=among%3Fthe%3FNTLM%3Fprotocols&flags=sp&limit=100000&sessions=70012701874
            
            payload = {'msg':'msearch','search': query_string}
            if(sessions):
                payload["sessions"]=sessions
                
            if(limit):
                payload["limit"]=limit
            if(flags):
                payload["flags"]=flags
            if(where):
                payload["where"]=where
            response = self.session.get(self.url+"/sdk",params=payload)

           
            _json_data = json.loads(response.content.decode("utf-8"))
            final_list =[] 
            for x in _json_data:
                final_list += x["results"]["fields"]
            df2 = pd.json_normalize(final_list)
            return df2