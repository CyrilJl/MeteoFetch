:notoc: true

Disponibilité des modèles
=========================

.. raw:: html

    <style>
        table {
            border-collapse: collapse;
            width: 100%;
        }
        th, td {
            border: 1px solid #dddddd;
            text-align: center;
            padding: 8px;
        }
        th {
            background-color: #f2f2f2;
            text-align: center;
        }
        th:first-child {
            text-align: center;
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

Aifs
~~~~

.. raw:: html

    <div id="status-aifs"></div>

Météo-France
------------

Arpège
~~~~~~

Arpege 0.1°
+++++++++++

.. raw:: html

    <div id="status-arpege01"></div>

Arpege 0.25°
++++++++++++

.. raw:: html

    <div id="status-arpege025"></div>

Arome
~~~~~

Arome 0.01°
+++++++++++

.. raw:: html

    <div id="status-arome001"></div>

Arome 0.025°
++++++++++++

.. raw:: html

    <div id="status-arome0025"></div>

Arome Outre-Mer
~~~~~~~~~~~~~~~

Arome Outre-Mer Antilles
++++++++++++++++++++++++

.. raw:: html

    <div id="status-arome-om-antilles"></div>

Arome Outre-Mer Guyane
++++++++++++++++++++++

.. raw:: html

    <div id="status-arome-om-guyane"></div>

Arome Outre-Mer Indien
++++++++++++++++++++++

.. raw:: html

    <div id="status-arome-om-indien"></div>

Arome Outre-Mer Nouvelle-Calédonie
++++++++++++++++++++++++++++++++++

.. raw:: html

    <div id="status-arome-om-nouvelle-caledonie"></div>

Arome Outre-Mer Polynésie
+++++++++++++++++++++++++

.. raw:: html

    <div id="status-arome-om-polynesie"></div>

.. raw:: html

    <script src="_static/js/status.js"></script>
