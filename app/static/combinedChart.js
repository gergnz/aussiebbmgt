function toggledark() {
  var colour = getCookie("colour");
  if (colour === "dark") {
    document.cookie = "colour=light";
    $("#cadence").removeClass("dark-input");
    $('input[type=text]').removeClass("dark-input");
    $('input[type=password]').removeClass("dark-input");
    $("#modalcontent").removeClass("dark-mode");
    var element = document.body;
    element.classList.remove("dark-mode");
  } else {
    document.cookie = "colour=dark";
    $("#cadence").addClass("dark-input");
    $('input[type=text]').addClass("dark-input");
    $('input[type=password]').addClass("dark-input");
    $("#modalcontent").addClass("dark-mode");
    var element = document.body;
    element.classList.add("dark-mode");
  }
}

function getCookie(cname) {
  var name = cname + "=";
  var ca = document.cookie.split(';');
  for(var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

var combinedChart;

function getChartData(url, fromdate = '', todate = '') {
    var speedurl = url + "/speedtestresults";
    var query = {};
    if (fromdate !== '') {
        query["fromdate"] = fromdate;
    }
    if (todate !== '') {
        query["todate"] = todate;
    }

    var imgheight = $( document ).width() / 3;

    $("#loadingMessage").html('<img src="/static/giphy.gif" height="'+imgheight+'" alt="" srcset="">');
    $.getJSON({
        url: speedurl,
        data: query,
        success: function(result) {
            var data = [];
            var up = [];
            var down = [];
            result.forEach(function(element) {
                down.push({
                    x: new Date(element.date),
                    y: element.downloadSpeedKbps
                });
                up.push({
                    x: new Date(element.date),
                    y: element.uploadSpeedKbps
                });
            });
            data.push(down);
            data.push(up);
            getnextChartData(url, data, fromdate, todate);
        },
        error: function(err) {
            $("#combinedChart").hide();
            $("#loadingMessage").html('<h3 class="display-1 text-danger text-left">Error!!!!<br>Something went wrong!</h3>');
        }
    });
}

function getnextChartData(url, speeddata, fromdate = '', todate = '') {
    var dpuurl = url + "/dputestresults";
    var query = {};
    if (fromdate !== '') {
        query["fromdate"] = fromdate;
    }
    if (todate !== '') {
        query["todate"] = todate;
    }
    $.getJSON({
        url: dpuurl,
        data: query,
        success: function(result) {
            $("#loadingMessage").html("");
            var data = speeddata;
            var up = [];
            var down = [];
            result.forEach(function(element) {
                down.push({
                    x: new Date(element.completed_at),
                    y: element.lineratedown * 1024
                });
                up.push({
                    x: new Date(element.completed_at),
                    y: element.linerateup * 1024
                });
            });
            data.push(down);
            data.push(up);
            renderChart(data);
        },
        error: function(err) {
            $("#combinedChart").hide();
            $("#loadingMessage").html('<h3 class="display-1 text-danger text-left">Error!!!!<br>Something went wrong!</h3>');
        }
    });
}

function getdata(url, fromdate, todate) {
        var rawfromdate = $("#fromdatepicker").val();
        if (rawfromdate !== '') {
            var zrawfromdate = rawfromdate.split('/');
            fromdate = new Date(zrawfromdate[2], zrawfromdate[1]-1, zrawfromdate[0]).toISOString();
        }
        var rawtodate = $("#todatepicker").val();
        if (rawtodate !== '') {
            var zrawtodate = rawtodate.split('/');
            var todate_raw = new Date(zrawtodate[2], zrawtodate[1]-1, zrawtodate[0]);
            todate = new Date(todate_raw.setDate(todate_raw.getDate() + 1)).toISOString();
        }
        getChartData(url, fromdate, todate);
}

function hello(response) {
  var proto = window.location.protocol;
  var port = window.location.port;
  var hostname = window.location.hostname;

  var url = proto + '//' + hostname + ':' + port;

  if (response.length == 1) {
    // do the charge as we have a username
    var todate = ''
    var fromdate = ''
    getChartData(url);

    $(function() {
        $("#fromdatepicker").datepicker({ dateFormat: "dd/mm/yy", minDate: "-12M", maxDate: "+0D" });
    });
    $(function() {
        $("#todatepicker").datepicker({ dateFormat: "dd/mm/yy", minDate: "-12M", maxDate: "+0D" });
    });

    $("#todatepicker").change(function() {$("#combinedChart").hide(); getdata(url, fromdate, todate)});
    $("#fromdatepicker").change(function() {$("#combinedChart").hide(); getdata(url, fromdate, todate)});

    setInterval(function(){
      getdata(url, fromdate, todate)
    }, 1800000);

  } else {
    var configtext = "<h4>Please enter your Aussie Broadband username and password to get started.</h4>";
    $("#loadingMessage").html(configtext);
    var userpass = `
        <div class="col-md-auto">
              <div class="row" id='userpass'>
                <div class="col">
                    <label for="aussiebb_username" class="form-label">Username:</label>
                    <input type="text" size="50" class="form-control" id="aussiebb_username">
                    <label for="aussiebb_password" class="form-label">Password:</label>
                    <input type="password" size="50" class="form-control" id="aussiebb_password">
                </div>
              </div>
              <div class="row pt-3" id='saveuserpassfirst'>
                <div class="col">
                    <button type="button" class="form-control btn btn-sm btn-outline-success">Save</button>
                </div>
              </div>
        </div>`;
    $("#datechooser").html(userpass);
    var colour = getCookie('colour');
    if (colour === 'dark') {
      $('input[type=text]').addClass("dark-input");
      $('input[type=password]').addClass("dark-input");
    };
    $("#saveuserpassfirst").click(function() {
        $.post(url+"/settings", data="aussiebb_username="+$("#aussiebb_username").val()+"&aussiebb_password="+encodeURIComponent($("#aussiebb_password").val()))
        .done(function() {
          location.reload();
        });
    });
  }
}

$(document).ready(function() {
    var proto = window.location.protocol;
    var port = window.location.port;
    var hostname = window.location.hostname;

    var url = proto + '//' + hostname + ':' + port;

    var aussiebb_username = $.getJSON({url: url+'/settings?key=aussiebb_username'})
      .done(hello);

    var colour = getCookie('colour');
    if (colour === 'dark') {
      $("#cadence").addClass("dark-input");
      $('input[type=text]').addClass("dark-input");
      $('input[type=password]').addClass("dark-input");
      $("#modalcontent").addClass("dark-mode");
      var element = document.body;
      element.classList.add("dark-mode");
    };

    $.getJSON({url: url+'/settings?key=cadence'})
      .done(function(data) {
      if (data.length == 1) {
          $("#cadence").val(data[0].value);
      } else {
          $("#cadence").val(24);
      }
    });

    $("#configuration").change(function() {
        $.post(url+"/settings", data="cadence="+$("#cadence").val())
    });

    $("#saveuserpass").click(function() {
        $.post(url+"/settings", data="aussiebb_username="+$("#aussiebb_username").val()+"&aussiebb_password="+encodeURIComponent($("#aussiebb_password").val()))
        .done(function() {
          $("#ConfigurationModal").modal('hide');
        });
    });        
});

function renderChart(data) {

    $("#combinedChart").show();

    if (combinedChart) {
      var i;
      for (i = 0; i < combinedChart.data.datasets.length; i++) {
          combinedChart.data.datasets[i].data = data[i];
      }
      combinedChart.update();
    } else {
        var ctx = document.getElementById("combinedChart").getContext('2d');
        combinedChart = new Chart(ctx, {
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
                plugins: {
                  legend: { position: 'bottom' }
                },
                scales: {
                    xAxis: {
                      type: 'time',
                      grid: { color: 'rgba(100, 100, 100, 1)'},
                    },
                    yAxis: {
                        grid: { color: 'rgba(100, 100, 100, 1)'},
                        title: {
                            display: true,
                            text: 'kbps'
                        },
                        beginAtZero: true
                    }
                }
            },
        });
    }
}
