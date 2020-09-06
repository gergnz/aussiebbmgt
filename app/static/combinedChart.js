function getChartData(url) {
    $("#loadingMessage").html('<img src="/static/giphy.gif" alt="" srcset="">');
    $.getJSON({
        url: url+"/speedtestresults?fromdate=2020-08-01T00:00:00",
        success: function (result) {
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
            getnextChartData(url, data);
        },
        error: function (err) {
            $("#loadingSpeedMessage").html("Error");
        }
    });
}
function getnextChartData(url, speeddata) {
    $.getJSON({
        url: url+"/dputestresults?fromdate=2020-08-01T00:00:00",
        success: function (result) {
            $("#loadingMessage").html("");
            var data = speeddata;
            var up = [];        
            var down = [];
            result.forEach(function(element){
              down.push({
                t: new Date(element.completed_at),
                y: element.lineratedown * 1024
              });
              up.push({
                t: new Date(element.completed_at),
                y: element.linerateup * 1024
              });
            });
            data.push(down);
            data.push(up);
            renderChart(data);
        },
        error: function (err) {
            $("#loadingMessage").html("Error");
        }
    });
}

$(document).ready(function(){
    var proto = window.location.protocol;
    var port = window.location.port;
    var hostname = window.location.hostname;
    url = proto+'//'+hostname+':'+port;
    getChartData(url);
    $( function() {
      $( "#fromdatepicker" ).datepicker();
    });
    $( function() {
      $( "#todatepicker" ).datepicker();
    });
    $( "#target" ).click(function() {
			try	{
			    var fromdate = new Date($("#fromdatepicker").val()).toISOString();
			}
			finally {}
			try {
			    var todate = new Date($("#todatepicker").val()).toISOString();
			}
			finally {}
    });
});

function renderChart(data) {
    var ctx = document.getElementById("combinedChart").getContext('2d');
    var combinedChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Download Speed',
                order: 0,
                fill: false,
                data: data[0],
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                pointRadius: 2
            },
            {
                label: 'Upload Speed',
                order: 1,
                fill: false,
                data: data[1],
                borderColor: 'rgba(192, 192, 192, 1)',
                backgroundColor: 'rgba(192, 192, 192, 1)',
                borderWidth: 1,
                pointRadius: 2
            },
            {
                label: 'Down Line Sync',
                order: 0,
                fill: false,
                data: data[2],
                borderColor: 'rgba(3, 7, 252, 1)',
                backgroundColor: 'rgba(3, 7, 252, 1)',
                borderWidth: 1,
                pointRadius: 2
            },
            {
                label: 'Up Line Sync',
                order: 1,
                fill: false,
                data: data[3],
                borderColor: 'rgba(252, 23, 3, 1)',
                backgroundColor: 'rgba(252, 23, 3, 1)',
                borderWidth: 1,
                pointRadius: 2
            },
            ]
        },
        options: {            
            scales: {
                xAxes: [{
                    type: 'time'
                }],
                yAxes: [{
                    scaleLabel: {
                      display: true,
                      labelString: 'kbps'
                    },
                    ticks: {
                        beginAtZero: true,
                    }
                }]
            }
        }
    });
}
