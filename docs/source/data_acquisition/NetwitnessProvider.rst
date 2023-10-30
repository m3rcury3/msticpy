Netwitness Provider
==================

Netwitness Configuration
-----------------------

You can store your connection details in *msticpyconfig.yaml*.

For more information on using and configuring *msticpyconfig.yaml* see
:doc:`msticpy Package Configuration <../getting_started/msticpyconfig>`
and :doc:`MSTICPy Settings Editor<../getting_started/SettingsEditor>`

The settings in the file should look like the following:

.. code:: yaml

    DataProviders:
        Netwitness:
            Args:
                nwhost: str() # IP Address of the Netwitness node to query (e.g. Broker or Concentrator service)
                nwport: str() # The REST API Port number (e.g. 50103 for a Broker service)
                nwuser: str() # The username to connect with

Loading a QueryProvider for Netwitness
-------------------------------------------

.. code:: ipython3

    qry_prov = QueryProvider("Netwitness")

Connecting to Netwitness
-----------------------------

The parameters required for connection to Netwitness can be passed in
a number of ways. The simplest is to configure your settings
in msticpyconfig. You can then just call connect with only the password because it is not included in the config file.

Alternatively, you can pass the required connection parameters
to the driver as parameters to the driver.

.. code:: ipython3

        qry_prov.connect(nwhost="NetwitnessHostname",nwport="RestAPIPort",nwuser="NetwitnessUsername",nwpassword="NetwitnessPassword")

Running a Netwitness query
-------------------------

To list the available queries:

.. code:: ipython3

    qry_prov.list_queries()

To display the help menu for a query (generic_query for example):

.. code:: ipython3

    qry_prov.GenericQueries.generic_query("?")

Example for running a query that displays the time, ip.src, ip.dst in the timewindow '2023-10-25 00:00:00' - '2023-10-25 01:00:00' where ip.src is 192.168.1.1:

.. code:: ipython3

    alerts=qry_prov.GenericQueries.generic_query(select_fields="time,ip.src,ip.dst",where_clause="time= '2023-10-25 00:00:00' - '2023-10-25 01:00:00' && ip.dst=192.168.1.1")
    alerts.head()