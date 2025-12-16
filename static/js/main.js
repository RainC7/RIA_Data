document.addEventListener('DOMContentLoaded', () => {
    const tableBody = document.getElementById('landmarksTable')?.getElementsByTagName('tbody')[0];
    const searchInput = document.getElementById('searchInput');
    const datasetCards = document.querySelectorAll('.dataset-card');
    const resultsCount = document.getElementById('resultsCount');
    const filterStatus = document.getElementById('filterStatus');
    const refreshButton = document.getElementById('refreshButton');
    const landmarkEmptyState = document.getElementById('emptyState');
    const landmarkExplorer = document.getElementById('landmarkExplorer');

    const railwayList = document.getElementById('railwayList');
    const railwayResultsCount = document.getElementById('railwayResultsCount');
    const railwayFilterStatus = document.getElementById('railwayFilterStatus');
    const railwayEmptyState = document.getElementById('railwayEmptyState');
    const railwaySearchInput = document.getElementById('railwaySearchInput');

    const serverControls = document.querySelectorAll('[data-server-control]');

    let currentServer = serverControls[0]?.value || 'zth';
    let landmarkDebounce;
    let railwayDebounce;

    function setActiveDatasetCard(server) {
        datasetCards.forEach(card => {
            card.classList.toggle('active', card.dataset.source === server);
        });
    }

    function syncServerControls(value, trigger) {
        currentServer = value;
        serverControls.forEach(control => {
            if (control !== trigger) {
                control.value = value;
            }
        });
        setActiveDatasetCard(value);
    }

    function updateDatasetCount(type, server, count) {
        document
            .querySelectorAll(`[data-count-type="${type}"][data-count-server="${server}"]`)
            .forEach(node => {
                node.textContent = typeof count === 'number' ? count : '--';
            });
    }

    function updateLandmarkMeta(count, searchTerm) {
        if (resultsCount) {
            resultsCount.textContent = `${count} 条记录`;
        }
        if (filterStatus) {
            filterStatus.textContent = `筛选条件：${searchTerm || '无'}`;
        }
    }

    function toggleLandmarkEmptyState(visible, message) {
        if (!landmarkEmptyState) return;
        landmarkEmptyState.hidden = !visible;
        const text = landmarkEmptyState.querySelector('p');
        if (text && message) {
            text.textContent = message;
        }
    }

    function renderLandmarkTable(data) {
        if (!tableBody) {
            return;
        }
        tableBody.innerHTML = '';
        if (!data.length) {
            toggleLandmarkEmptyState(true, '暂无符合条件的地标。');
            return;
        }
        toggleLandmarkEmptyState(false);
        data.forEach(landmark => {
            const row = tableBody.insertRow();
            row.insertCell(0).innerText = landmark.id;
            row.insertCell(1).innerText = landmark.name;
            row.insertCell(2).innerText = landmark.grade;
            row.insertCell(3).innerText = landmark.status;
            const coordinates = landmark.coordinates || {};
            row.insertCell(4).innerText = `(${coordinates.x ?? 'Unknown'}, ${coordinates.y ?? 'Unknown'}, ${coordinates.z ?? 'Unknown'})`;
        });
    }

    async function fetchLandmarks() {
        const searchTerm = searchInput?.value.trim() || '';
        const params = new URLSearchParams({ server: currentServer });
        if (searchTerm) {
            params.append('name', searchTerm);
        }
        try {
            const response = await fetch(`/api/landmarks?${params.toString()}`);
            const data = await response.json();
            renderLandmarkTable(data);
            updateLandmarkMeta(data.length, searchTerm);
        } catch (error) {
            console.error('Error loading landmark data:', error);
            toggleLandmarkEmptyState(true, '加载地标数据失败，请稍后重试。');
        }
    }

    function updateRailwayMeta(count, searchTerm) {
        if (railwayResultsCount) {
            railwayResultsCount.textContent = `${count} 个站点`;
        }
        if (railwayFilterStatus) {
            railwayFilterStatus.textContent = `筛选条件：${searchTerm || '无'}`;
        }
    }

    function toggleRailwayEmptyState(visible, message) {
        if (!railwayEmptyState) return;
        railwayEmptyState.hidden = !visible;
        const text = railwayEmptyState.querySelector('p');
        if (text && message) {
            text.textContent = message;
        }
    }

    function formatCoord(coord = {}) {
        return `(${coord.x ?? 'Unknown'}, ${coord.y ?? 'Unknown'}, ${coord.z ?? 'Unknown'})`;
    }

    function renderRailwayList(stations) {
        if (!railwayList) {
            return;
        }
        railwayList.innerHTML = '';
        if (!stations.length) {
            toggleRailwayEmptyState(true, '暂无符合条件的铁路网数据。');
            return;
        }
        toggleRailwayEmptyState(false);
        stations.forEach(station => {
            const card = document.createElement('article');
            card.className = 'railway-station-card';

            const header = document.createElement('div');
            header.className = 'station-title';
            const title = document.createElement('h3');
            title.textContent = station.stationName || '未命名站点';
            const badge = document.createElement('span');
            badge.className = 'badge badge-soft';
            badge.textContent = currentServer.toUpperCase();
            header.appendChild(title);
            header.appendChild(badge);
            card.appendChild(header);

            const lines = Array.isArray(station.lines) ? station.lines : [];
            const linesContainer = document.createElement('div');
            linesContainer.className = 'station-lines';

            if (lines.length === 0) {
                const placeholder = document.createElement('p');
                placeholder.className = 'line-code';
                placeholder.textContent = '暂无线路信息';
                linesContainer.appendChild(placeholder);
            } else {
                lines.forEach(line => {
                    const lineItem = document.createElement('div');
                    lineItem.className = 'station-line-item';
                    const name = document.createElement('div');
                    name.className = 'line-name';
                    name.textContent = `${line.bureau || '-'} · ${line.line || '-'} 线`;

                    const code = document.createElement('div');
                    code.className = 'line-code';
                    code.textContent = `站码：${line.stationCode || '-'}`;

                    const coord = document.createElement('div');
                    coord.className = 'line-coord';
                    coord.textContent = formatCoord(line.coord);

                    lineItem.appendChild(name);
                    lineItem.appendChild(code);
                    lineItem.appendChild(coord);
                    linesContainer.appendChild(lineItem);
                });
            }

            card.appendChild(linesContainer);
            railwayList.appendChild(card);
        });
    }

    async function fetchRailways() {
        const searchTerm = railwaySearchInput?.value.trim() || '';
        const params = new URLSearchParams({ server: currentServer });
        if (searchTerm) {
            params.append('name', searchTerm);
        }
        try {
            const response = await fetch(`/api/railways?${params.toString()}`);
            const data = await response.json();
            renderRailwayList(data);
            updateRailwayMeta(data.length, searchTerm);
        } catch (error) {
            console.error('Error loading railway data:', error);
            toggleRailwayEmptyState(true, '加载铁路网数据失败，请稍后重试。');
        }
    }

    async function preloadDatasetStatistics() {
        const servers = Array.from(new Set(Array.from(datasetCards).map(card => card.dataset.source).filter(Boolean)));
        for (const server of servers) {
            try {
                const [landmarksResp, railwayResp] = await Promise.all([
                    fetch(`/api/landmarks?server=${server}`),
                    fetch(`/api/railways?server=${server}`)
                ]);
                const [landmarks, railways] = await Promise.all([
                    landmarksResp.json(),
                    railwayResp.json()
                ]);
                updateDatasetCount('landmark', server, landmarks.length);
                updateDatasetCount('railway', server, railways.length);
            } catch (error) {
                console.warn(`Failed to preload stats for ${server}`, error);
                updateDatasetCount('landmark', server, '--');
                updateDatasetCount('railway', server, '--');
            }
        }
    }

    datasetCards.forEach(card => {
        card.addEventListener('click', () => {
            const server = card.dataset.source;
            if (!server) return;
            syncServerControls(server);
            fetchLandmarks();
            fetchRailways();
            landmarkExplorer?.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    serverControls.forEach(control => {
        control.addEventListener('change', event => {
            const value = event.target.value;
            syncServerControls(value, control);
            fetchLandmarks();
            fetchRailways();
        });
    });

    searchInput?.addEventListener('input', () => {
        clearTimeout(landmarkDebounce);
        landmarkDebounce = setTimeout(fetchLandmarks, 300);
    });

    railwaySearchInput?.addEventListener('input', () => {
        clearTimeout(railwayDebounce);
        railwayDebounce = setTimeout(fetchRailways, 300);
    });

    refreshButton?.addEventListener('click', () => {
        fetchLandmarks();
        fetchRailways();
    });

    syncServerControls(currentServer);
    fetchLandmarks();
    fetchRailways();
    preloadDatasetStatistics();
});
