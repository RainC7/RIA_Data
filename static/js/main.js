document.addEventListener('DOMContentLoaded', function() {
    const landmarksTable = document.getElementById('landmarksTable').getElementsByTagName('tbody')[0];
    const searchInput = document.getElementById('searchInput');
    const dataSourceSelect = document.getElementById('dataSourceSelect');
    let landmarksData = [];

    function fetchData() {
        const selectedSource = dataSourceSelect.value;
        const searchTerm = searchInput.value.toLowerCase();
        fetch(`/api/landmarks?source=${selectedSource}&name=${searchTerm}`)
            .then(response => response.json())
            .then(data => {
                landmarksData = data;
                renderTable(landmarksData);
            })
            .catch(error => console.error('Error loading landmark data:', error));
    }

    fetchData(); // Initial data load

    function renderTable(data) {
        landmarksTable.innerHTML = '';
        data.forEach(landmark => {
            let row = landmarksTable.insertRow();
            row.insertCell(0).innerText = landmark.id;
            row.insertCell(1).innerText = landmark.name;
            row.insertCell(2).innerText = landmark.grade;
            row.insertCell(3).innerText = landmark.status;
            row.insertCell(4).innerText = `(${landmark.coordinates.x}, ${landmark.coordinates.y}, ${landmark.coordinates.z})`;
        });
    }

    searchInput.addEventListener('input', fetchData);
    dataSourceSelect.addEventListener('change', fetchData);
});