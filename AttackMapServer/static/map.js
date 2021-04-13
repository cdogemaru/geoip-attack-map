// To access by a browser in another computer, use the external IP of machine running AttackMapServer
// from the same computer(only), you can use the internal IP.
// Example:
// - AttackMapServer machine:
//   - Internal IP: 127.0.0.1
//   - External IP: 192.168.11.106
// var webSock = new WebSocket("ws:/192.168.1.137:8888/websocket"); // Internal
var webSock = new WebSocket("ws:/166.111.68.233:43241/websocket"); // Internal

L.mapbox.accessToken = 'pk.eyJ1IjoiY2RvZ2VtYXJ1IiwiYSI6ImNrbXc2a29veDBieXoydnFudnAwcHd2NWQifQ.p7fS86vrdu0OY5bS-xLocw';
var map = L.mapbox.map("map", "mapbox.dark", {
    center: [10, -40], // lat, long
    zoom: 2,
    zoomControl: false
});

var svg = d3.select(map.getPanes().tilePane).append("svg")
    .attr("class", "leaflet-zoom-animated")
    .attr("width", window.innerWidth)
    .attr("height", window.innerHeight)
    .attr("pointer-events", "auto");

// function translateSVG() {
//     var viewBoxLeft = document.querySelector("svg.leaflet-zoom-animated").viewBox.animVal.x;
//     var viewBoxTop = document.querySelector("svg.leaflet-zoom-animated").viewBox.animVal.y;

//     // Resizing width and height in case of window resize
//     svg.attr("width", window.innerWidth);
//     svg.attr("height", window.innerHeight);

//     // Adding the ViewBox attribute to our SVG to contain it
//     svg.attr("viewBox", function () {
//         return "" + viewBoxLeft + " " + viewBoxTop + " "  + window.innerWidth + " " + window.innerHeight;
//     });

//     // Adding the style attribute to our SVG to translate it
//     svg.attr("style", function () {
//         return "transform: translate3d(" + viewBoxLeft + "px, " + viewBoxTop + "px, 0px);";
//     });
// }

// function update() {
//     console.log("updating");
//     translateSVG();
// }

// map.on("moveend", update);

$(function () {
    console.log("test");
    $("#legend-table").mCustomScrollbar({
        theme: "rounded-dark",
        autoHideScrollbar: false
    });
    $("#attack-table").mCustomScrollbar({
        theme: "rounded-dark",
        autoHideScrollbar: false
    });
});

function calcMidpoint(x1, y1, x2, y2, bend) {
    var tmpx = (x1 + x2) / 2;
    var tmpy = (y1 + y2) / 2;
    var dx = y2 - y1;
    var dy = x1 - x2;
    var r = Math.random() / 6 + 0.05;
    var a = tmpx + r * dx;
    var b = tmpy + r * dy;
    return {"x":a, "y":b};
}

function translateAlong(path) {
    var l = path.getTotalLength();
    return function(i) {
        return function(t) {
            // Put in try/catch because sometimes floating point is stupid..
            try {
            var p = path.getPointAtLength(t*l);
            return "translate(" + p.x + "," + p.y + ")";
            } catch(err){
            console.log("Caught exception.");
            return "ERROR";
            }
        }
    }
}

function prependCVERow(id, args) {
    var tr = document.createElement('tr');
    tr.setAttribute("id", id + '-' + args[7]);
    tr.onclick = function () {
        alert(args[9]);
        data_url = "/data/";
        data = {
            alarm_id: args[9]
        };
        $.post(data_url, data, function (res, status) {
            console.log(res);
            try {
                var msg = JSON.parse(res.data);
                console.log(msg);
                handleAbnormalPaths(msg);
                handleNormalPaths(msg);
                setTimeout(function () {
                    svg.selectAll("*")
                        .transition()
                        .duration(1000)
                        .style('opacity', 0)
                        .remove();
                    svg.selectAll("*").remove();
                    for (var i = 0; i < markers.length; i++) {
                        map.removeLayer(markers[i]);
                    }
                }, 7000);
                handleLegendType(msg);
                handle
            } catch (err) {
                console.log(err)
            }
        });
    };
    count = 1;

    for (var i = 0; i < count; i++) {
        var td = document.createElement('td');

        // Timestamp
        var textNode = document.createTextNode(args[0]);
        td.appendChild(textNode);
        tr.appendChild(td);

        // attacker ASN
        var td = document.createElement('td');
        var textNode = document.createTextNode(args[7]);
        td.appendChild(textNode);
        tr.appendChild(td);

        var td = document.createElement('td');

        var path = 'flags/' + args[2] + '.png';
        var img = document.createElement('img');
        img.src = path;
        td.appendChild(img);
        tr.appendChild(td);

        var td = document.createElement('td');
        var textNode = document.createTextNode(args[4]);
        td.appendChild(textNode);
        tr.appendChild(td);

        // victim ASN        
        var td = document.createElement('td');
        var textNode = document.createTextNode(args[8]);
        td.appendChild(textNode);
        tr.appendChild(td);

        // victim location
        var td = document.createElement('td');
        var path = 'flags/' + args[5] + '.png';
        var img = document.createElement('img');
        img.src = path;
        td.appendChild(img);
        tr.appendChild(td);

        var td = document.createElement('td');
        var textNode = document.createTextNode(args[6]);
        td.appendChild(textNode);
        tr.appendChild(td);

        // Hijacked prefix
        var td = document.createElement('td');
        var textNode = document.createTextNode(args[3]);
        td.appendChild(textNode);
        tr.appendChild(td);

    }

    var element = document.getElementById(id);
    var rowCount = element.rows.length;

    // Only allow 50 rows
    if (rowCount >= 50) {
        element.deleteRow(rowCount -1);
    }

    element.insertBefore(tr, element.firstChild);
}

function prependLegendRow(id) {
    fnames = ["attacker.svg", "target.svg", "eye.svg", "red_line.svg", "green_line.svg"];
    texts = ["Attacker", "Victim", "Vantage Point", "Hijacked Path", "Normal Path"];

    var element = document.getElementById(id);
    for (var i = 0; i < fnames.length; i++) {
        var tr = document.createElement('tr');

        // legend
        var td = document.createElement('td');
        var path = 'static/' + fnames[i];
        var img = document.createElement('img');
        img.src = path;
        img.setAttribute("style", "width:20%;");
        td.appendChild(img);
        tr.appendChild(td);

        // text
        var td = document.createElement('td');
        var textNode = document.createTextNode(texts[i]);
        td.appendChild(textNode);
        tr.appendChild(td);

        element.insertBefore(tr, element.firstChild);
    }

}
prependLegendRow('attack-legendresp');

function handleLegendType(msg) {
    if (msg.attack_type == 1) {
        var attackType = ["Origin Hijacking"];
    } else {
        var attackType = ["Path Hijacking"]
    }
    // TODO add event time

    var now = new Date();
    var year = now.getFullYear(); //得到年份
    var month = now.getMonth();//得到月份
    var date = now.getDate();//得到日期
    var hour = now.getHours();//得到小时
    var minu = now.getMinutes();//得到分钟
    var sec = now.getSeconds();//得到秒

    if (hour < 10) {
        hour = "0" + hour;
    }
    if (minu < 10) {
        minu = "0" + minu;
    }
    if (sec < 10) {
        sec = "0" + sec;
    }

    var time = year + "-" + month + "-" + date + " " + hour + ":" + minu + ":" + sec;

    var attackCve = [
            time,//msg.event_time,
            attackType,
            msg.attacker_country_code,
            msg.prefix,
            msg.attacker_country_name,
            msg.victim_country_code,
            msg.victim_country_name,
            msg.attacker,
            msg.victim,
            msg.alarm_id // Note: modified by maq18
            ];
    prependCVERow('attack-cveresp', attackCve);

}

function transitionNext(i, _index, msg, is_abnormal) {
    if (is_abnormal) {
        path = msg.abnormal_path_geos[i];
    } else {
        path = msg.normal_path_geos[i];
    }

    if (_index + 1 > path.length - 1) {
        return;
    }
    var lastpoint = path[_index];
    var curpoint = path[_index + 1];

    var lastgeo = new L.LatLng(lastpoint[1], lastpoint[0]);
    var curgeo = new L.LatLng(curpoint[1], curpoint[0]);

    lastpoint = map.latLngToLayerPoint(lastgeo);
    curpoint = map.latLngToLayerPoint(curgeo);

    if (is_abnormal) {
        var color = "#FF0000"
    } else {
        var color = "#9ede73"
    }

    var x = curpoint['x'];
    var y = curpoint['y'];
    svg.append('circle')
        .attr('cx', x)
        .attr('cy', y)
        .attr('r', 3)
        .style('fill', 'none')
        .style('stroke', color)
        .style('stroke-opacity', 1)
        .transition()
        .duration(700)
        .ease(Math.sqrt)
        .attr('r', 6)
        .style('stroke-opacity', 1e-6)
        .remove();

    var fromX = lastpoint['x'];
    var fromY = lastpoint['y'];
    var toX = curpoint['x'];
    var toY = curpoint['y'];
    var bendArray = [true, false];
    var bend = 0;

    var lineData = [lastpoint, calcMidpoint(fromX, fromY, toX, toY, bend), curpoint];
    var lineFunction = d3.line()
    // var lineFunction = d3.svg.line()
        // .interpolate("basis")
        .curve(d3.curveBasis)
        .x(function (d) { return d.x; })
        .y(function (d) { return d.y; });

    var lineGraph = svg.append('path')
        .attr('d', lineFunction(lineData))
        .attr('opacity', 0.8)
        .attr('stroke', color)
        .attr('stroke-width', 2)
        .attr('fill', 'none');

    if (translateAlong(lineGraph.node()) === 'ERROR') {
        console.log('translateAlong ERROR')
        return;
    }

    var circleRadius = 6

    // // Circle follows the line
    // var dot = svg.append('circle')
    //     // .data({ "long": path[_index + 1][0], "lati": path[_index + 1][1] })
    //     .attr('r', 3)
    //     .attr('fill', color)
    //     .transition()
    //         .duration(600)
    //         .ease(d3.easeSin)
    //         .attrTween('transform', translateAlong(lineGraph.node()));

    var length = lineGraph.node().getTotalLength();
    lineGraph.attr('stroke-dasharray', length + ' ' + length)
        .attr('stroke-dashoffset', length)
        .transition()
            .duration(600)
            .ease(d3.easeSin)
            .attr('stroke-dashoffset', 0)
            .on('end', function () {
                _index = _index + 1;
                transitionNext(i, _index, msg, is_abnormal);
            });
}

var circles = new L.LayerGroup();
map.addLayer(circles);

function addCircle(color, fillcolor, srcLatLng) {
    circleCount = circles.getLayers().length;
    circleArray = circles.getLayers();

    // Only allow 50 circles to be on the map at a time
    if (circleCount >= 50) {
        circles.removeLayer(circleArray[0]);
    }

    L.circle(srcLatLng, {
        color: color,
        fillColor: fillcolor,
        fillOpacity: 0.2,
        radius: 100000
    }).addTo(circles);
}

var markers = [];
function handleAbnormalPaths(msg) {

    var path_num = Math.min(msg.abnormal_path_geos.length, 3);

    var end_node_edges = [];
    var lineGraphs = [];
    var dots = [];

    var end_r_low = 4;
    var mid_r = 2;
    var end_r_up = 12;
    var dur = 1000;
    var color = "#ff0000";
    var vp_color = "#ffcc29";
    var cnt = 0;

    var yratio = 0.6;
    var xratio = 2;


    var eyeicon = L.icon({
        iconUrl: '/static/eye.svg',
        // iconUrl: '/static/eye.svg',
        iconSize: [36, 36], // size of the icon
        iconAnchor: [18, 38], // point of the icon which will correspond to marker's location
    });
    var attackericon = L.icon({
        iconUrl: '/static/attacker.svg',
        iconSize: [38, 35], // size of the icon
        iconAnchor: [19, 45], // point of the icon which will correspond to marker's location
    });

    var myIcon = L.divIcon({ className: 'my-div-icon' });
    // you can set .my-div-icon styles in CSS
    var popupContent = "test";
    for (var i = 0; i < path_num; i++) {
        var path = msg.abnormal_path_geos[i];
        var attacker = path[0];
        var attackergeo = new L.LatLng(attacker[1], attacker[0]);
        var a = L.marker(attackergeo, {
            title: "Attacker",
            icon: attackericon,
            // new L.DivIcon({
            //     className: 'my-div-icon',
            //     html: '<img class="my-div-image" src="/static/attacker.svg"/>' +
            //         '<span class="my-div-span">RAF Banff Airfield</span>'
            // })
            opacity: 1
        }).addTo(map).bindPopup(popupContent);;

        var vp = path[path.length - 1];
        var vpgeo = new L.LatLng(vp[1], vp[0]);
        var b = L.marker(vpgeo, {
            title: "Vantage Point",
            icon: eyeicon,
            opacity: 1
        }).addTo(map);

        markers.push(a);
        markers.push(b);

    }

    for (var i = 0; i < path_num; i++) {
        var path = msg.abnormal_path_geos[i];
        for (var j = 0; j < path.length - 1; j++) {
            var last_node = path[j];
            var cur_node = path[j + 1];


            var lastgeo = new L.LatLng(last_node[1], last_node[0]);
            var curgeo = new L.LatLng(cur_node[1], cur_node[0]);

            var lastpoint = map.latLngToLayerPoint(lastgeo);
            var curpoint = map.latLngToLayerPoint(curgeo);


            var toX = lastpoint['x'];
            var toY = lastpoint['y'];
            var fromX = curpoint['x'];
            var fromY = curpoint['y'];



            var bend = 0;

            var lineData = [curpoint, calcMidpoint(fromX, fromY, toX, toY, bend), lastpoint];
            var lineFunction = d3.line()
                .curve(d3.curveBasis)
                .x(function (d) { return d.x; })
                .y(function (d) { return d.y; });

            var lineGraph = svg.append('path')
                .attr('d', lineFunction(lineData))
                .attr('opacity', 1e-6)
                .attr('stroke', color)
                .attr('stroke-width', 2)
                .attr('fill', 'none');

            var dot = svg.append('circle')
            lineGraphs.push(lineGraph);
            dots.push(dot);

            if (translateAlong(lineGraph.node()) === 'ERROR') {
                console.log('translateAlong ERROR')
                return;
            }

            var length = lineGraph.node().getTotalLength();
            lineGraph.attr('stroke-dasharray', length + ' ' + length)
                .attr('stroke-dashoffset', 0)
                .transition()
                .duration(dur)
                .attr('opacity', 0.8);

            if (j == path.length - 2) {

                var x = curpoint['x'];
                var y = curpoint['y'];
                var end_node_edge = svg.append('ellipse')
                    .attr('cx', x)
                    .attr('cy', y)
                    // .attr('r', end_r_low)
                    .attr('rx', xratio * end_r_low)
                    .attr('ry', yratio * end_r_low)
                    .style('fill', 'none')
                    .style('stroke', vp_color);

                end_node_edges.push(end_node_edge);

                var end_node = svg.append('ellipse')
                    .attr('cx', x)
                    .attr('cy', y)
                    // .attr('r', end_r_low)
                    .attr('rx', xratio * end_r_low)
                    .attr('ry', yratio * end_r_low)
                    .style('fill', vp_color)
                    .style('stroke', vp_color)
                    .style('stroke-opacity', 1e-6)
                    .transition()
                    .duration(dur)
                    .ease(Math.sqrt)
                    .style('stroke-opacity', 1);


                if (i == path_num - 1) {
                    end_node.on("end", function () {
                        console.log(lineGraphs);
                        for (var k = 0; k < end_node_edges.length; k++) {
                            end_node_edges[k]
                                .style('stroke-opacity', 1)
                                .attr('rx', xratio * end_r_low)
                                .attr('ry', yratio * end_r_low)
                                // .attr('r', end_r_low)
                                .transition()
                                .duration(dur)
                                .ease(Math.sqrt)
                                .style('stroke-opacity', 1e-6)
                                .on('end', function repeat_end_node() {
                                    d3.select(this)
                                        .style('stroke-opacity', 1)
                                        // .attr('r', end_r_low)
                                        .attr('rx', xratio * end_r_low)
                                        .attr('ry', yratio * end_r_low)
                                        .transition()
                                        .duration(dur)
                                        .ease(Math.sqrt)
                                        // .attr('r', end_r_up)
                                        .attr('rx', xratio * end_r_up)
                                        .attr('ry', yratio * end_r_up)
                                        .style('stroke-opacity', 1e-6)
                                        .on('end', repeat_end_node);
                                });
                        }
                        for (var k = 0; k < dots.length; k++) {
                            for (var t = 0; t < 6; t++) {
                                dots[k]
                                    .attr('r', 3)
                                    .attr('fill', color)
                                    .transition()
                                    .duration(dur)
                                    .delay(dur * t)
                                    .ease(d3.easeSin)
                                    .attrTween('transform', translateAlong(lineGraphs[k].node()));
                                // .on('end', repeat_line(k));
                            }
                        }
                    })
                }
            }
            else {
                if (j == 0) {


                    var x = lastpoint['x'];
                    var y = lastpoint['y'];
                    var init_node_edge = svg.append('ellipse')
                        .attr('cx', x)
                        .attr('cy', y)
                        .attr('rx', xratio * end_r_low)
                        .attr('ry', yratio * end_r_low)
                        .style('fill', 'none')
                        .style('stroke', color);
                    // var init_node_edge = svg.append('circle')
                    //     .attr('cx', x)
                    //     .attr('cy', y)
                    //     .attr('r', end_r_low)
                    //     .style('fill', 'none')
                    //     .style('stroke', color);

                    var init_node = svg.append('ellipse')
                        .attr('cx', x)
                        .attr('cy', y)
                        .attr('rx', xratio * end_r_low)
                        .attr('ry', yratio * end_r_low)
                        // .attr('r', end_r_low)
                        .style('fill', color)
                        .style('stroke', color)
                        .style('stroke-opacity', 1e-6)
                        .transition()
                        .duration(dur)
                        .ease(Math.sqrt)
                        .style('stroke-opacity', 1e-6)
                        .on("end", function repeat_init_node() {
                            init_node_edge
                                .style('stroke-opacity', 1)
                                .attr('rx', xratio * end_r_low)
                                .attr('ry', yratio * end_r_low)
                                // .attr('r', end_r_low)
                                .transition()
                                .duration(dur)
                                .ease(Math.sqrt)
                                // .attr('r', end_r_up)
                                .attr('rx', xratio * end_r_up)
                                .attr('ry', yratio * end_r_up)
                                .style('stroke-opacity', 1e-6)
                                .on('end', repeat_init_node);
                        });
                }
                var x = curpoint['x'];
                var y = curpoint['y'];
                svg.append('ellipse')
                    .attr('cx', x)
                    .attr('cy', y)
                    // .attr('r', mid_r)

                    .attr('rx', xratio * mid_r)
                    .attr('ry', yratio * mid_r)
                    .style('fill', color)
                    .style('stroke', color)
                    .style('stroke-opacity', 1e-6)
                    .transition()
                    .duration(dur)
                    .ease(Math.sqrt)
                    .style('stroke-opacity', 1);
            }
        }
    }
}

function handleNormalPaths(msg) {

    var path_num = Math.min(msg.normal_path_geos.length, 3);

    var end_node_edges = [];
    var lineGraphs = [];
    var dots = [];

    var end_r_low = 4;
    var mid_r = 2;
    var end_r_up = 12;
    var dur = 1000;
    var color = "#81b214";
    var vp_color = "#ffcc29";
    var cnt = 0;

    var yratio = 0.6;
    var xratio = 2;


    var eyeicon = L.icon({
        iconUrl: '/static/eye.svg',
        // iconUrl: '/static/eye.svg',
        iconSize: [36, 36], // size of the icon
        iconAnchor: [18, 38], // point of the icon which will correspond to marker's location
    });
    var victimicon = L.icon({
        iconUrl: '/static/target.svg',
        iconSize: [38, 35], // size of the icon
        iconAnchor: [19, 45], // point of the icon which will correspond to marker's location
    });

    var myIcon = L.divIcon({ className: 'my-div-icon' });
    // you can set .my-div-icon styles in CSS
    var popupContent = "test";
    for (var i = 0; i < path_num; i++) {
        var path = msg.normal_path_geos[i];
        var attacker = path[0];
        var attackergeo = new L.LatLng(attacker[1], attacker[0]);
        var a = L.marker(attackergeo, {
            title: "Attacker",
            icon: victimicon,
            // new L.DivIcon({
            //     className: 'my-div-icon',
            //     html: '<img class="my-div-image" src="/static/attacker.svg"/>' +
            //         '<span class="my-div-span">RAF Banff Airfield</span>'
            // })
            opacity: 1
        }).addTo(map).bindPopup(popupContent);
        // var a = L.marker(attackergeo).addTo(map).bindPopup(popupContent);

        var vp = path[path.length - 1];
        var vpgeo = new L.LatLng(vp[1], vp[0]);
        var b = L.marker(vpgeo, {
            title: "Vantage Point",
            icon: eyeicon,
            opacity: 1
        }).addTo(map);

        markers.push(a);
        markers.push(b);

    }

    for (var i = 0; i < path_num; i++) {
        var path = msg.normal_path_geos[i];
        for (var j = 0; j < path.length - 1; j++) {
            var last_node = path[j];
            var cur_node = path[j + 1];


            var lastgeo = new L.LatLng(last_node[1], last_node[0]);
            var curgeo = new L.LatLng(cur_node[1], cur_node[0]);

            var lastpoint = map.latLngToLayerPoint(lastgeo);
            var curpoint = map.latLngToLayerPoint(curgeo);


            var toX = lastpoint['x'];
            var toY = lastpoint['y'];
            var fromX = curpoint['x'];
            var fromY = curpoint['y'];



            var bend = 0;

            var lineData = [curpoint, calcMidpoint(fromX, fromY, toX, toY, bend), lastpoint];
            var lineFunction = d3.line()
                .curve(d3.curveBasis)
                .x(function (d) { return d.x; })
                .y(function (d) { return d.y; });

            var lineGraph = svg.append('path')
                .attr('d', lineFunction(lineData))
                .attr('opacity', 1e-6)
                .attr('stroke', color)
                .attr('stroke-width', 2)
                .attr('fill', 'none');

            var dot = svg.append('circle')
            lineGraphs.push(lineGraph);
            dots.push(dot);

            if (translateAlong(lineGraph.node()) === 'ERROR') {
                console.log('translateAlong ERROR')
                return;
            }

            var length = lineGraph.node().getTotalLength();
            lineGraph.attr('stroke-dasharray', length + ' ' + length)
                .attr('stroke-dashoffset', 0)
                .transition()
                .duration(dur)
                .attr('opacity', 0.8);

            if (j == path.length - 2) {

                var x = curpoint['x'];
                var y = curpoint['y'];
                var end_node_edge = svg.append('ellipse')
                    .attr('cx', x)
                    .attr('cy', y)
                    // .attr('r', end_r_low)
                    .attr('rx', xratio * end_r_low)
                    .attr('ry', yratio * end_r_low)
                    .style('fill', 'none')
                    .style('stroke', vp_color);

                end_node_edges.push(end_node_edge);

                var end_node = svg.append('ellipse')
                    .attr('cx', x)
                    .attr('cy', y)
                    // .attr('r', end_r_low)
                    .attr('rx', xratio * end_r_low)
                    .attr('ry', yratio * end_r_low)
                    .style('fill', vp_color)
                    .style('stroke', vp_color)
                    .style('stroke-opacity', 1e-6)
                    .transition()
                    .duration(dur)
                    .ease(Math.sqrt)
                    .style('stroke-opacity', 1);


                if (i == path_num - 1) {
                    end_node.on("end", function () {
                        console.log(lineGraphs);
                        for (var k = 0; k < end_node_edges.length; k++) {
                            end_node_edges[k]
                                .style('stroke-opacity', 1)
                                .attr('rx', xratio * end_r_low)
                                .attr('ry', yratio * end_r_low)
                                // .attr('r', end_r_low)
                                .transition()
                                .duration(dur)
                                .ease(Math.sqrt)
                                .style('stroke-opacity', 1e-6)
                                .on('end', function repeat_end_node() {
                                    d3.select(this)
                                        .style('stroke-opacity', 1)
                                        // .attr('r', end_r_low)
                                        .attr('rx', xratio * end_r_low)
                                        .attr('ry', yratio * end_r_low)
                                        .transition()
                                        .duration(dur)
                                        .ease(Math.sqrt)
                                        // .attr('r', end_r_up)
                                        .attr('rx', xratio * end_r_up)
                                        .attr('ry', yratio * end_r_up)
                                        .style('stroke-opacity', 1e-6)
                                        .on('end', repeat_end_node);
                                });
                        }
                        for (var k = 0; k < dots.length; k++) {
                            for (var t = 0; t < 6; t++) {
                                dots[k]
                                    .attr('r', 3)
                                    .attr('fill', color)
                                    .transition()
                                    .duration(dur)
                                    .delay(dur * t)
                                    .ease(d3.easeSin)
                                    .attrTween('transform', translateAlong(lineGraphs[k].node()));
                                // .on('end', repeat_line(k));
                            }
                        }
                    })
                }
            }
            else {
                if (j == 0) {


                    var x = lastpoint['x'];
                    var y = lastpoint['y'];
                    var init_node_edge = svg.append('ellipse')
                        .attr('cx', x)
                        .attr('cy', y)
                        .attr('rx', xratio * end_r_low)
                        .attr('ry', yratio * end_r_low)
                        .style('fill', 'none')
                        .style('stroke', color);
                    // var init_node_edge = svg.append('circle')
                    //     .attr('cx', x)
                    //     .attr('cy', y)
                    //     .attr('r', end_r_low)
                    //     .style('fill', 'none')
                    //     .style('stroke', color);

                    var init_node = svg.append('ellipse')
                        .attr('cx', x)
                        .attr('cy', y)
                        .attr('rx', xratio * end_r_low)
                        .attr('ry', yratio * end_r_low)
                        // .attr('r', end_r_low)
                        .style('fill', color)
                        .style('stroke', color)
                        .style('stroke-opacity', 1e-6)
                        .transition()
                        .duration(dur)
                        .ease(Math.sqrt)
                        .style('stroke-opacity', 1e-6)
                        .on("end", function repeat_init_node() {
                            init_node_edge
                                .style('stroke-opacity', 1)
                                .attr('rx', xratio * end_r_low)
                                .attr('ry', yratio * end_r_low)
                                // .attr('r', end_r_low)
                                .transition()
                                .duration(dur)
                                .ease(Math.sqrt)
                                // .attr('r', end_r_up)
                                .attr('rx', xratio * end_r_up)
                                .attr('ry', yratio * end_r_up)
                                .style('stroke-opacity', 1e-6)
                                .on('end', repeat_init_node);
                        });
                }
                var x = curpoint['x'];
                var y = curpoint['y'];
                svg.append('ellipse')
                    .attr('cx', x)
                    .attr('cy', y)
                    // .attr('r', mid_r)

                    .attr('rx', xratio * mid_r)
                    .attr('ry', yratio * mid_r)
                    .style('fill', color)
                    .style('stroke', color)
                    .style('stroke-opacity', 1e-6)
                    .transition()
                    .duration(dur)
                    .ease(Math.sqrt)
                    .style('stroke-opacity', 1);
            }
        }
    }
}

webSock.onmessage = function (e) {
    console.log("Got a websocket message...");
    try {
        var msg = JSON.parse(e.data);
        console.log(msg);     
        handleAbnormalPaths(msg);
        handleNormalPaths(msg);

        setTimeout(function () {
            svg.selectAll("*")
                .transition()
                .duration(1000)
                .style('opacity', 0)
                .remove();
            svg.selectAll("*").remove();
            for(var i = 0; i < markers.length; i ++) {
                map.removeLayer(markers[i]);
            }
        }, 7000);
        handleLegendType(msg);
    } catch(err) {
        console.log(err)
    }
};

$(document).on("click","#informIP #exit", function (e) {
    $("#informIP").hide();
});

$(document).on("click", '.container-fluid .showInfo', function(e) {
    var iplink = $(this).text();
    $("#informIP").show();
    $("#informIP").html( "<a id='ip_only' href='"+iplink+"'></a><button id='exit'>X</button><h3>"+iplink+"</h3><br><ul><li><a target = '_blank' href='http://www.senderbase.org/lookup/?search_string="+iplink+"'><b><u color=white>Senderbase</a></li><li><a target='_blank' href='https://ers.trendmicro.com/reputations/index'>Trend Micro</a></li><li><a target='_blank' href='http://www.anti-abuse.org/multi-rbl-check-results/?host="+iplink+"'>Anti-abuse</a></li></ul><br><button id='blockIP' alt='"+iplink+"'>Block IP</button>   ");
});

$(document).on("click","#informIP #blockIP", function (e) {
    var ip= $(this).attr('alt');
    var ipBlocked = "ip_blocked:"+ip;
    console.log("Sending message: "+ipBlocked);
    webSock.send(ipBlocked);
});
