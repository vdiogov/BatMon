function renderCharts(serviceId, chartLabels, responseTimeData, uptimeData) {
    // Response Time Chart
    var rtCtx = document.getElementById('responseTimeChart-' + serviceId).getContext('2d');
    new Chart(rtCtx, {
        type: 'line',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Response Time (s)',
                data: responseTimeData,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                borderWidth: 1,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Response Time (s)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });

    // Uptime Chart
    var upCtx = document.getElementById('uptimeChart-' + serviceId).getContext('2d');
    new Chart(upCtx, {
        type: 'bar',
        data: {
            labels: chartLabels,
            datasets: [{
                label: 'Uptime (1=Up, 0=Down)',
                data: uptimeData,
                backgroundColor: function(context) {
                    var value = context.dataset.data[context.dataIndex];
                    return value === 1 ? 'rgba(75, 192, 192, 0.8)' : 'rgba(255, 99, 132, 0.8)';
                },
                borderColor: function(context) {
                    var value = context.dataset.data[context.dataIndex];
                    return value === 1 ? 'rgba(75, 192, 192, 1)' : 'rgba(255, 99, 132, 1)';
                },
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        stepSize: 1
                    },
                    title: {
                        display: true,
                        text: 'Status'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Time'
                    }
                }
            }
        }
    });
}