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

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const models = {
                'ifs': {
                    name: 'Ifs',
                    containerId: 'status-ifs',
                    baseUrl: 'https://data.ecmwf.int/ecpds/home/opendata/{ymd}/{hour}z/ifs/0p25/oper/{ymd}{hour}0000-{group}h-oper-fc.grib2',
                    freqUpdate: 12,
                    pastRuns: 4,
                    groups: [...Array(49).keys()].map(i => i * 3), // 0, 3, 6, ..., 144
                    getUrls: function(date, group) {
                        const ymd = date.toISOString().slice(0, 10).replace(/-/g, '');
                        const hour = date.getUTCHours().toString().padStart(2, '0');
                        const url = this.baseUrl
                            .replace(/{ymd}/g, ymd)
                            .replace(/{hour}/g, hour)
                            .replace(/{group}/g, group);
                        return [url];
                    }
                },
                'arome001': {
                    name: 'Arome 0.01°',
                    containerId: 'status-arome001',
                    baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome/001/{paquet}/arome__001__{paquet}__{group}__{date}:00:00Z.grib2',
                    freqUpdate: 3,
                    pastRuns: 4,
                    paquets: ['SP1', 'SP2', 'SP3', 'HP1'],
                    groups: Array.from({ length: 52 }, (_, i) => `${String(i).padStart(2, '0')}H`),
                    getUrls: function(date, paquet) {
                        const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                        return this.groups.map(group => {
                            return this.baseUrl
                                .replace(/{date}/g, dateStr)
                                .replace(/{paquet}/g, paquet)
                                .replace(/{group}/g, group);
                        });
                    }
                },
                'arpege01': {
                    name: 'Arpege 0.1°',
                    containerId: 'status-arpege01',
                    baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arpege/01/{paquet}/arpege__01__{paquet}__{group}__{date}:00:00Z.grib2',
                    freqUpdate: 6,
                    pastRuns: 4,
                    paquets: ['SP1', 'SP2', 'IP1', 'IP2', 'IP3', 'IP4', 'HP1', 'HP2'],
                    groups: ["000H012H", "013H024H", "025H036H", "037H048H", "049H060H", "061H072H", "073H084H", "085H096H", "097H102H"],
                    getUrls: function(date, paquet) {
                        const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                        return this.groups.map(group => {
                            return this.baseUrl
                                .replace(/{date}/g, dateStr)
                                .replace(/{paquet}/g, paquet)
                                .replace(/{group}/g, group);
                        });
                    }
                }
            };

            function checkUrl(url) {
                return fetch(url, { method: 'HEAD' })
                    .then(response => response.ok)
                    .catch(() => false);
            }

            function checkUrls(urls) {
                return Promise.all(urls.map(checkUrl)).then(results => results.every(r => r));
            }

            function createTable(model) {
                const container = document.getElementById(model.containerId);
                if (!container) return;

                const paquets = model.paquets || [model.name];
                const table = document.createElement('table');
                const thead = document.createElement('thead');
                const tbody = document.createElement('tbody');

                let headerRow = '<tr><th>Run (UTC)</th>';
                paquets.forEach(p => headerRow += `<th>${p}</th>`);
                headerRow += '</tr>';
                thead.innerHTML = headerRow;
                table.appendChild(thead);

                const now = new Date();
                let latestRun = new Date(Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate(), Math.floor(now.getUTCHours() / model.freqUpdate) * model.freqUpdate));

                for (let i = 0; i < model.pastRuns; i++) {
                    const runDate = new Date(latestRun.getTime() - i * model.freqUpdate * 60 * 60 * 1000);
                    const row = document.createElement('tr');
                    const dateCell = `<td>${runDate.toISOString().replace('T', ' ').slice(0, 16)}</td>`;
                    row.innerHTML = dateCell;

                    paquets.forEach(paquet => {
                        const cell = document.createElement('td');
                        cell.className = 'status-cell';
                        cell.innerHTML = '<div class="lds-dual-ring"></div>';
                        row.appendChild(cell);

                        const urls = model.getUrls(runDate, paquet);
                        checkUrls(urls).then(isAvailable => {
                            cell.innerHTML = isAvailable ? '✅' : '❌';
                            cell.classList.add(isAvailable ? 'status-ok' : 'status-ko');
                        });
                    });

                    tbody.appendChild(row);
                }

                table.appendChild(tbody);
                container.innerHTML = '';
                container.appendChild(table);
            }

            Object.values(models).forEach(createTable);
        });
    </script>
