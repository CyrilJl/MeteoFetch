document.addEventListener('DOMContentLoaded', () => {
    // Helper function for Arome Outre Mer models
    const getAromeOMGroups = function (paquet) {
        if (paquet === "IP4" || paquet === "HP3") {
            return this.groups.slice(1);
        }
        return this.groups;
    };

    const models = {
        'ifs': {
            name: 'Ifs',
            containerId: 'status-ifs',
            baseUrl: 'https://data.ecmwf.int/ecpds/home/opendata/{ymd}/{hour}z/ifs/0p25/oper/{ymd}{hour}0000-{group}h-oper-fc.grib2',
            freqUpdate: 12,
            pastRuns: 4,
            groups: [...[...Array(49).keys()].map(i => i * 3), ...[...Array(13).keys()].map(i => 150 + i * 6)],
            getUrls: function (date) {
                const ymd = date.toISOString().slice(0, 10).replace(/-/g, '');
                const hour = date.getUTCHours().toString().padStart(2, '0');
                // For IFS, we check a few key groups, not all of them to avoid too many requests
                const groupsToCheck = [this.groups[0], this.groups[10], this.groups[20], this.groups[this.groups.length - 1]];
                return groupsToCheck.map(group => {
                    return this.baseUrl
                        .replace(/{ymd}/g, ymd)
                        .replace(/{hour}/g, hour)
                        .replace(/{group}/g, group);
                });
            }
        },
        'aifs': {
            name: 'Aifs',
            containerId: 'status-aifs',
            baseUrl: 'https://data.ecmwf.int/forecasts/{ymd}/{hour}z/aifs-single/0p25/oper/{ymd}{hour}0000-{group}h-oper-fc.grib2',
            freqUpdate: 6,
            pastRuns: 4,
            groups: Array.from({ length: 42 }, (_, i) => i * 6),
            getUrls: function (date) {
                const ymd = date.toISOString().slice(0, 10).replace(/-/g, '');
                const hour = date.getUTCHours().toString().padStart(2, '0');
                const groupsToCheck = [this.groups[0], this.groups[10], this.groups[20], this.groups[this.groups.length - 1]];
                return groupsToCheck.map(group => {
                    return this.baseUrl
                        .replace(/{ymd}/g, ymd)
                        .replace(/{hour}/g, hour)
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
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                return this.groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
        'arpege025': {
            name: 'Arpege 0.25°',
            containerId: 'status-arpege025',
            baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arpege/025/{paquet}/arpege__025__{paquet}__{group}__{date}:00:00Z.grib2',
            freqUpdate: 6,
            pastRuns: 4,
            paquets: ['SP1', 'SP2', 'IP1', 'IP2', 'IP3', 'IP4', 'HP1', 'HP2'],
            groups: ["000H024H", "025H048H", "049H072H", "073H102H"],
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                return this.groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
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
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                return this.groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
        'arome0025': {
            name: 'Arome 0.025°',
            containerId: 'status-arome0025',
            baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome/0025/{paquet}/arome__0025__{paquet}__{group}__{date}:00:00Z.grib2',
            freqUpdate: 3,
            pastRuns: 4,
            paquets: ["SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3"],
            groups: ["00H06H", "07H12H", "13H18H", "19H24H", "25H30H", "31H36H", "37H42H", "43H48H", "49H51H"],
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                return this.groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
        'arome-om-antilles': {
            name: 'Arome Outre-Mer Antilles',
            containerId: 'status-arome-om-antilles',
            baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome-om/ANTIL/0025/{paquet}/arome-om-ANTIL__0025__{paquet}__{group}__{date}:00:00Z.grib2',
            freqUpdate: 3,
            pastRuns: 4,
            paquets: ["SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3"],
            groups: Array.from({ length: 49 }, (_, i) => `${String(i).padStart(3, '0')}H`),
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                const groups = getAromeOMGroups.call(this, paquet);
                return groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
        'arome-om-guyane': {
            name: 'Arome Outre-Mer Guyane',
            containerId: 'status-arome-om-guyane',
            baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome-om/GUYANE/0025/{paquet}/arome-om-GUYANE__0025__{paquet}__{group}__{date}:00:00Z.grib2',
            freqUpdate: 3,
            pastRuns: 4,
            paquets: ["SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3"],
            groups: Array.from({ length: 49 }, (_, i) => `${String(i).padStart(3, '0')}H`),
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                const groups = getAromeOMGroups.call(this, paquet);
                return groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
        'arome-om-indien': {
            name: 'Arome Outre-Mer Indien',
            containerId: 'status-arome-om-indien',
            baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome-om/INDIEN/0025/{paquet}/arome-om-INDIEN__0025__{paquet}__{group}__{date}:00:00Z.grib2',
            freqUpdate: 3,
            pastRuns: 4,
            paquets: ["SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3"],
            groups: Array.from({ length: 49 }, (_, i) => `${String(i).padStart(3, '0')}H`),
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                const groups = getAromeOMGroups.call(this, paquet);
                return groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
        'arome-om-nouvelle-caledonie': {
            name: 'Arome Outre-Mer Nouvelle-Calédonie',
            containerId: 'status-arome-om-nouvelle-caledonie',
            baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome-om/NCALED/0025/{paquet}/arome-om-NCALED__0025__{paquet}__{group}__{date}:00:00Z.grib2',
            freqUpdate: 3,
            pastRuns: 4,
            paquets: ["SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3"],
            groups: Array.from({ length: 49 }, (_, i) => `${String(i).padStart(3, '0')}H`),
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                const groups = getAromeOMGroups.call(this, paquet);
                return groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
        'arome-om-polynesie': {
            name: 'Arome Outre-Mer Polynésie',
            containerId: 'status-arome-om-polynesie',
            baseUrl: 'https://object.data.gouv.fr/meteofrance-pnt/pnt/{date}:00:00Z/arome-om/POLYN/0025/{paquet}/arome-om-POLYN__0025__{paquet}__{group}__{date}:00:00Z.grib2',
            freqUpdate: 3,
            pastRuns: 4,
            paquets: ["SP1", "SP2", "SP3", "IP1", "IP2", "IP3", "IP4", "IP5", "HP1", "HP2", "HP3"],
            groups: Array.from({ length: 49 }, (_, i) => `${String(i).padStart(3, '0')}H`),
            getUrls: function (date, paquet) {
                const dateStr = `${date.toISOString().slice(0, 10)}T${String(date.getUTCHours()).padStart(2, '0')}`;
                const groups = getAromeOMGroups.call(this, paquet);
                return groups.map(group => {
                    return this.baseUrl
                        .replace(/{date}/g, dateStr)
                        .replace(/{paquet}/g, paquet)
                        .replace(/{group}/g, group);
                });
            }
        },
    };

    async function checkUrl(url) {
        try {
            const response = await fetch(url, { method: 'HEAD' });
            return response.ok;
        } catch {
            return false;
        }
    }

    async function checkUrls(urls) {
        const chunkSize = 10;
        const delay = 100; // ms
        for (let i = 0; i < urls.length; i += chunkSize) {
            const chunk = urls.slice(i, i + chunkSize);
            const results = await Promise.all(chunk.map(checkUrl));
            if (results.some(r => !r)) {
                return false;
            }
            if (i + chunkSize < urls.length) {
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
        return true;
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
