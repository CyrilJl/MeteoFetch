Statut des modèles
===================

.. raw:: html

    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
        }
        .status-cell {
            text-align: center;
            font-weight: bold;
        }
        .status-ok {
            background-color: #c8e6c9; /* Green */
        }
        .status-ko {
            background-color: #ffcdd2; /* Red */
        }
        .lds-dual-ring {
            display: inline-block;
            width: 15px;
            height: 15px;
        }
        .lds-dual-ring:after {
            content: " ";
            display: block;
            width: 15px;
            height: 15px;
            margin: 0px;
            border-radius: 50%;
            border: 3px solid #fff;
            border-color: #000 transparent #000 transparent;
            animation: lds-dual-ring 1.2s linear infinite;
        }
        @keyframes lds-dual-ring {
            0% {
                transform: rotate(0deg);
            }
            100% {
                transform: rotate(360deg);
            }
        }
    </style>

ECMWF
-----

Ifs
~~~

.. raw:: html

    <div id="status-ifs"></div>

Météo-France
------------

Arome 0.01°
~~~~~~~~~~~~

.. raw:: html

    <div id="status-arome001"></div>

Arpege 0.1°
~~~~~~~~~~~

.. raw:: html

    <div id="status-arpege01"></div>

.. raw:: html

    <script src="_static/js/status.js"></script>
