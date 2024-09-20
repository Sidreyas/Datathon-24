// File: static/js/scripts.js

$(document).ready(function() {
    // Initialize global variables for chart instances
    let trendChartInstance = null;
    let typeChartInstance = null;

    // Function to populate the Year filter dynamically
    function populateYearFilter() {
        $.getJSON('/api/recent_detections', function(data) {
            let years = new Set();
            data.forEach(function(detection) {
                let year = new Date(detection.timestamp).getFullYear();
                years.add(year);
            });
            let yearOptions = Array.from(years).sort((a, b) => b - a);
            yearOptions.forEach(function(year) {
                $('#filterYear').append(`<option value="${year}">${year}</option>`);
            });
        }).fail(function() {
            console.error("Failed to fetch recent detections for Year filter.");
        });
    }

    // Function to apply filters and update the dashboard
    function applyFilters() {
        let year = $('#filterYear').val();
        let month = $('#filterMonth').val();
        let media_type = $('#filterMediaType').val();
        let status = $('#filterStatus').val();

        // Fetch and update recent detections table
        $.getJSON('/api/recent_detections_filtered', { year, month, media_type, status }, function(filteredData) {
            var tableBody = $('#detectionsTable tbody');
            tableBody.empty();  // Clear existing data
            if (filteredData.length === 0) {
                tableBody.append('<tr><td colspan="6" class="text-center">No records found.</td></tr>');
            } else {
                filteredData.forEach(function(detection) {
                    var row = '<tr>' +
                              `<td>${detection.id}</td>` +
                              `<td>${detection.media_type}</td>` +
                              `<td>${detection.timestamp}</td>` +
                              `<td>${detection.status}</td>` +
                              `<td>${(detection.confidence_score * 100).toFixed(2)}%</td>` +
                              `<td>${detection.details}</td>` +
                              '</tr>';
                    tableBody.append(row);
                });
            }
        }).fail(function() {
            console.error("Failed to fetch filtered detections.");
        });

        // Update charts based on filters
        loadTrendChart(year, month);
        loadTypeChart(year, month);
    }

    // Function to reset all filters
    function resetFilters() {
        $('#filterYear').val('');
        $('#filterMonth').val('');
        $('#filterMediaType').val('');
        $('#filterStatus').val('');
        applyFilters();  // Reload dashboard with all data
    }

    // Function to load overview metrics
    function loadOverview() {
        $.getJSON('/api/overview', function(data) {
            $('#total_media').text(data.total_media_processed);
            $('#total_deepfakes').text(data.total_deepfakes_detected);
            $('#detection_accuracy').text(data.detection_accuracy + '%');
            $('#false_positives').text(data.false_positives);
            $('#false_negatives').text(data.false_negatives);
        }).fail(function() {
            console.error("Failed to fetch overview metrics.");
        });
    }

    // Function to load and render the Trend Chart
    function loadTrendChart(year = null, month = null) {
        let endpoint = '/api/trend_data_filtered';
        let params = {};

        if (year) params.year = year;
        if (month) params.month = month;

        $.getJSON(endpoint, params, function(data) {
            var ctx = document.getElementById('trendChart').getContext('2d');
            // Destroy existing chart instance if it exists
            if (trendChartInstance) {
                trendChartInstance.destroy();
            }
            trendChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: data.dates,
                    datasets: [{
                        label: 'Deepfake Detections',
                        data: data.detections,
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        borderColor:'rgba(255, 99, 132, 1)',
                        borderWidth: 1,
                        fill: true,
                        lineTension: 0.3,
                        pointRadius: 3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        xAxes: [{
                            type: 'time',
                            time: {
                                unit: 'day',
                                tooltipFormat: 'll'
                            },
                            distribution: 'linear'
                        }],
                        yAxes: [{
                            ticks: {
                                beginAtZero: true,
                                precision:0
                            }
                        }]
                    },
                    tooltips: {
                        mode: 'index',
                        intersect: false,
                    },
                    hover: {
                        mode: 'nearest',
                        intersect: true
                    }
                }
            });
        }).fail(function() {
            console.error("Failed to fetch trend data.");
        });
    }

    // Function to load and render the Deepfake Types Pie Chart
    function loadTypeChart(year = null, month = null) {
        let endpoint = '/api/deepfake_types_filtered'; // Assume you have this endpoint to get filtered types
        let params = {};

        if (year) params.year = year;
        if (month) params.month = month;

        $.getJSON(endpoint, params, function(data) {
            var ctx = document.getElementById('typeChart').getContext('2d');
            // Destroy existing chart instance if it exists
            if (typeChartInstance) {
                typeChartInstance.destroy();
            }
            typeChartInstance = new Chart(ctx, {
                type: 'pie',
                data: {
                    labels: data.types,
                    datasets: [{
                        data: data.counts,
                        backgroundColor: [
                            'rgba(54, 162, 235, 0.6)',
                            'rgba(255, 206, 86, 0.6)',
                            'rgba(75, 192, 192, 0.6)',
                            'rgba(153, 102, 255, 0.6)',
                            'rgba(255, 159, 64, 0.6)'
                        ],
                        borderColor: [
                            'rgba(54, 162, 235, 1)',
                            'rgba(255, 206, 86, 1)',
                            'rgba(75, 192, 192, 1)',
                            'rgba(153, 102, 255, 1)',
                            'rgba(255, 159, 64, 1)'
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    legend: {
                        position: 'bottom'
                    },
                    tooltips: {
                        callbacks: {
                            label: function(tooltipItem, data) {
                                let dataset = data.datasets[tooltipItem.datasetIndex];
                                let total = dataset.data.reduce((prev, curr) => prev + curr);
                                let currentValue = dataset.data[tooltipItem.index];
                                let percentage = ((currentValue / total) * 100).toFixed(2);
                                return `${data.labels[tooltipItem.index]}: ${percentage}%`;
                            }
                        }
                    }
                }
            });
        }).fail(function() {
            console.error("Failed to fetch deepfake types data.");
        });
    }

    // Function to populate the Recent Detections Table initially
    function populateRecentDetections() {
        $.getJSON('/api/recent_detections', function(data) {
            var tableBody = $('#detectionsTable tbody');
            tableBody.empty();  // Clear existing data
            if (data.length === 0) {
                tableBody.append('<tr><td colspan="6" class="text-center">No records found.</td></tr>');
            } else {
                data.forEach(function(detection) {
                    var row = '<tr>' +
                              `<td>${detection.id}</td>` +
                              `<td>${detection.media_type}</td>` +
                              `<td>${detection.timestamp}</td>` +
                              `<td>${detection.status}</td>` +
                              `<td>${(detection.confidence_score * 100).toFixed(2)}%</td>` +
                              `<td>${detection.details}</td>` +
                              '</tr>';
                    tableBody.append(row);
                });
            }
        }).fail(function() {
            console.error("Failed to fetch recent detections.");
        });
    }

    // Function to handle Report Downloads
    function handleReportDownloads() {
        $('#downloadCSV').click(function() {
            let year = $('#filterYear').val();
            let month = $('#filterMonth').val();
            let media_type = $('#filterMediaType').val();
            let status = $('#filterStatus').val();

            let query = $.param({ format: 'csv', year, month, media_type, status });
            window.location.href = `/api/generate_report?${query}`;
        });

        $('#downloadPDF').click(function() {
            let year = $('#filterYear').val();
            let month = $('#filterMonth').val();
            let media_type = $('#filterMediaType').val();
            let status = $('#filterStatus').val();

            let query = $.param({ format: 'pdf', year, month, media_type, status });
            window.location.href = `/api/generate_report?${query}`;
        });
    }

    // Initialize all components
    function initializeDashboard() {
        populateYearFilter();
        loadOverview();
        loadTrendChart();
        loadTypeChart();
        populateRecentDetections();
        handleReportDownloads();
    }

    // Event Listeners for Filters
    $('#applyFilters').click(function() {
        applyFilters();
    });

    $('#resetFilters').click(function() {
        resetFilters();
    });

    // Initialize the dashboard on page load
    initializeDashboard();
});

