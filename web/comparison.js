
var get = {};
location.search.replace('?', '').split('&').forEach(function (val) {
    split = val.split("=", 2);

    if (get[split[0]] != undefined) {
        get[split[0]].push(split[1]);
    } else {
        get[split[0]] = [split[1]];
    }
});

if (get['comparison'] == undefined) {
    console.log('comparison[] is undefined!')
}

array = get['comparison']
count = 0
results = {}
branches = {}
dates = {}
$.each(array, function(index, value) {
    $.get('http://monetdb.cwi.nl/testweb/web/chronos/results/' + value, function(data) {
        var lines = data.split('\n');
        revision = "None";
        revisionlink = "None";
        branch = "None";
        database = "None";
        parameters = "";
        for(var i = 0; i < lines.length; i++) {
            if (lines[i].indexOf("branch:") > -1) {
                branch = lines[i].split(':')[1];
            } else if (lines[i].indexOf("revision:") > -1) {
                revision = lines[i].split(':')[1];
                if (results[revision] == undefined) {
                    results[revision] = {}
                }
            } else if (lines[i].indexOf("database:") > -1) {
                database = lines[i].split(':')[1];
            } else if (lines[i].indexOf("revisionlink:") > -1) {
                revisionlink = lines[i].split(':')[1];
            } else if (lines[i].indexOf("-mean:") > -1) {
                spl = lines[i].split("-mean:")
                results[revision][parameters]['mean'][spl[0]] = spl[1]
            } else if (lines[i].indexOf("-std:") > -1) {
                spl = lines[i].split("-mean:")
                results[revision][parameters]['std'][spl[0]] = spl[1]
            } else if (lines[i].indexOf("startresultblock:") > -1) {
                parameters = "";
            } else if (lines[i].indexOf("compileparameters:") > -1) {
                parameters += lines[i].split(':')[1] + ", "
            } else if (lines[i].indexOf("runtimeparameters:") > -1) {
                parameters += lines[i].split(/:(.+)?/)[1] + ", "
            } else if (lines[i].indexOf("startresults:") > -1) {
                parameters = parameters.substring(0, parameters.length - 2)
                results[revision][parameters] = { mean: {}, std: {}}
            }
        }
        branches[revision] = branch
        spl = value.split('.')
        if (spl.length > 2) {
            dates[revision] = value.split('.')[2]
        } else {
            dates[revision] = 0
        }
        count += 1
        if (count == array.length) {
            parameters = []
            revisions = []
            files = []
            $.each(results, function(index, value) {
                revisions.push(index);
                $.each(value, function(index2, value2) {
                    if ($.inArray(index2, parameters) < 0) {
                        parameters.push(index2)
                    }
                    $.each(value2['mean'], function(index3, value3) {
                        if ($.inArray(index3, files) < 0) {
                            files.push(index3)
                        }
                    });
                });
            });
            $.each(files, function(index, file) {
                $.each(parameters, function(index2, parameter) {
                    chartColors = d3.scale.category20()
                    chartdata = [];
                    local_branches = []
                    count = 0
                    $.each(revisions, function(index3, revision) {
                        val = results[revision][parameter]['mean'][file]
                        chartdata.push({ revision: revision, value: val, color: chartColors(count), branch: branches[revision], date: dates[revision] })
                        if ($.inArray(branches[revision], local_branches) < 0) {
                            local_branches.push(branches[revision])
                        }
                        count += 1
                    });
                    unique_branches = false
                    if (local_branches.length == chartdata.length) {
                        unique_branches = true
                    }
                    chartdata.sort(function(a,b) {
                        return a.date - b.date;
                    });

                    var margin = {top: 50, right: 50, bottom: 50, left: 50},
                        width = 75 * chartdata.length + 200 - margin.left - margin.right,
                        height = 400 - margin.top - margin.bottom;

                    var x = d3.scale.ordinal()
                        .rangeRoundBands([0, width], .1);

                    var y = d3.scale.linear()
                        .range([height, 0]);

                    var xAxis = d3.svg.axis()
                        .scale(x)
                        .orient("bottom");

                    var yAxis = d3.svg.axis()
                        .scale(y)
                        .orient("left");

                    var svg = d3.select("body").append("svg")
                        .attr("width", width + margin.left + margin.right)
                        .attr("height", height + margin.top + margin.bottom)
                        .append("g")
                        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

                    svg.append("text")
                        .attr("x", (width / 2))             
                        .attr("y", 0 - (margin.top / 2))
                        .attr("text-anchor", "middle")  
                        .style("font-size", "16px") 
                        .style("text-decoration", "underline")  
                        .text("Query " + file + " (" + parameter + ")");

                    x.domain(chartdata.map(function(d) { return unique_branches ? d.branch : d.revision; }));
                    y.domain([0, 1.3 * d3.max(chartdata, function(d) { return d.value; })]);

                    svg.append("g")
                        .attr("class", "x axis")
                        .attr("transform", "translate(0," + height + ")")
                        .call(xAxis);

                    svg.append("g")
                        .attr("class", "y axis")
                        .call(yAxis)
                        .append("text")
                        .attr("transform", "rotate(-90)")
                        .attr("y", 6)
                        .attr("dy", ".71em")
                        .style("text-anchor", "end")
                        .text("Time (s)");

                    svg.selectAll(".bar")
                        .data(chartdata)
                        .enter().append("rect")
                        .attr("class", "bar")
                        .attr("x", function(d) { return x(unique_branches ? d.branch : d.revision); })
                        .attr("width", x.rangeBand())
                        .attr("y", function(d) { return y(d.value); })
                        .attr("height", function(d) { return height - y(d.value); })
                        .style({fill:function(d){return d.color} })
                });
            });
            /* var ctx = $("#chart");
            */
        }
    });
});