function getSpeedChartData() {
    $("#loadingSpeedMessage").html('<img src="/static/giphy.gif" alt="" srcset="">');
    $.getJSON({
        url: "http://localhost:5000/speedtestresults",
        success: function (result) {
            $("#loadingSpeedMessage").html("");
            var data = [];
            var up = [];        
            var down = [];
            result.forEach(function(element){
              down.push({
                t: new Date(element.date),
                y: element.downloadSpeedKbps
              });
              up.push({
                t: new Date(element.date),
                y: element.uploadSpeedKbps
              });
            });
            data.push(down);
            data.push(up);
            renderSpeedChart(data);
        },
        error: function (err) {
            $("#loadingSpeedMessage").html("Error");
        }
    });
}

function getLinesyncChartData() {
    $("#loadingLinesyncMessage").html('<img src="/static/giphy.gif" alt="" srcset="">');
    $.getJSON({
        url: "http://localhost:5000/dputestresults",
        success: function (result) {
            $("#loadingLinesyncMessage").html("");
            var data = [];
            var up = [];        
            var down = [];
            result.forEach(function(element){
              down.push({
                t: new Date(element.completed_at),
                y: element.lineratedown
              });
              up.push({
                t: new Date(element.completed_at),
                y: element.linerateup
              });
            });
            data.push(down);
            data.push(up);
            renderLinesyncChart(data);
        },
        error: function (err) {
            $("#loadingLinesyncMessage").html("Error");
        }
    });
}

$(document).ready(function(){
     getSpeedChartData();
     getLinesyncChartData();
});

function renderSpeedChart(data) {
    var ctx = document.getElementById("speedChart").getContext('2d');
    var speedChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Download Speed',
                order: 0,
                fill: false,
                data: data[0],
                borderColor: 'rgba(75, 192, 192, 1)'
            },
            {
                label: 'Upload Speed',
                order: 1,
                fill: false,
                data: data[1],
                borderColor: 'rgba(192, 192, 192, 1)'
            },
            ]
        },
        options: {            
            scales: {
                xAxes: [{
                    type: 'time'
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                    }
                }]
            }
        }
    });
}

function renderLinesyncChart(data) {
    var ctx = document.getElementById("linesyncChart").getContext('2d');
    var linesyncChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Down Line Sync',
                order: 0,
                fill: false,
                data: data[0],
                borderColor: 'rgba(75, 192, 192, 1)'
            },
            {
                label: 'Up Line Sync',
                order: 1,
                fill: false,
                data: data[1],
                borderColor: 'rgba(192, 192, 192, 1)'
            },
            ]
        },
        options: {            
            scales: {
                xAxes: [{
                    type: 'time'
                }],
                yAxes: [{
                    ticks: {
                        beginAtZero: true,
                    }
                }]
            }
        }
    });
}
