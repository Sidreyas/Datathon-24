$(document).ready(function() {
    // Fetch and display overview metrics
    $.getJSON('/api/overview', function(data) {
        $('#total_media').text(data.total_media_processed);
        $('#total_deepfakes').text(data.total_deepfakes_detected);
        $('#detection_accuracy').text(data.detection_accuracy + '%');
        $('#false_positives').text(data.false_positives);
        $('#false_negatives').text(data.false_negatives);
    });
    
    // Fetch and render trend chart
    $.getJSON('/api/trend_data', function(data) {
        var ctx = document.getElementById('trendChart').getContext('2d');
        var trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.dates,
                datasets: [{
                    label: 'Deepfake Detections',
                    data: data.detections,
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    borderColor:'rgba(255, 99, 132, 1)',
                    borderWidth: 1,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
    
    // Fetch and render deepfake types pie chart
    $.getJSON('/api/deepfake_types', function(data) {
        var ctx = document.getElementById('typeChart').getContext('2d');
        var typeChart = new Chart(ctx, {
            type: 'pie',
            data: {
                labels: data.types,
                datasets: [{
                    data: data.counts,
                    backgroundColor: [
                        'rgba(54, 162, 235, 0.6)',
                        'rgba(255, 206, 86, 0.6)',
                        'rgba(75, 192, 192, 0.6)',
                        'rgba(153, 102, 255, 0.6)'
                    ],
                    borderColor: [
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false
            }
        });
    });
    
    // Fetch and populate recent detections table
    $.getJSON('/api/recent_detections', function(data) {
        var tableBody = $('#detectionsTable tbody');
        tableBody.empty();  // Clear existing data
        data.forEach(function(detection) {
            var row = '<tr>' +
                      '<td>' + detection.id + '</td>' +
                      '<td>' + detection.media_type + '</td>' +
                      '<td>' + detection.timestamp + '</td>' +
                      '<td>' + detection.status + '</td>' +
                      '<td>' + (detection.confidence_score * 100).toFixed(2) + '%</td>' +
                      '<td>' + detection.details + '</td>' +
                      '</tr>';
            tableBody.append(row);
        });
    });
});
