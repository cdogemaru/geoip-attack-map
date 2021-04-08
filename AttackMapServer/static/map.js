// To access by a browser in another computer, use the external IP of machine running AttackMapServer
// from the same computer(only), you can use the internal IP.
// Example:
// - AttackMapServer machine:
//   - Internal IP: 127.0.0.1
//   - External IP: 192.168.11.106
var webSock = new WebSocket("ws:/166.111.68.233:43241/websocket"); // Internal

L.mapbox.accessToken = 'pk.eyJ1IjoiY2RvZ2VtYXJ1IiwiYSI6ImNrbXc2a29veDBieXoydnFudnAwcHd2NWQifQ.p7fS86vrdu0OY5bS-xLocw';
var map = L.mapbox.map("map", "mapbox.dark", {
    center: [0, 0], // lat, long
    zoom: 2,
    zoomControl: false
});

// add full screen option
// L.control.fullscreen().addTo(map);

// hq coords
// var hqLatLng = new L.LatLng(-122.0881, 37.3845);

// // hq marker
// L.circle(hqLatLng, 110000, {
//     color: 'red',
//     fillColor: 'yellow',
//     fillOpacity: 0.5,
// }).addTo(map);

var svg = d3.select(map.getPanes().tilePane).append("svg")
    .attr("class", "leaflet-zoom-animated")
    .attr("width", window.innerWidth)
    .attr("height", window.innerHeight)
    .attr("pointer-events", "auto");

// function update1() {
// }

// map.on("zoomend", update1)

function translateSVG() {
    var viewBoxLeft = document.querySelector("svg.leaflet-zoom-animated").viewBox.animVal.x;
    var viewBoxTop = document.querySelector("svg.leaflet-zoom-animated").viewBox.animVal.y;

    // Resizing width and height in case of window resize
    svg.attr("width", window.innerWidth);
    svg.attr("height", window.innerHeight);

    // Adding the ViewBox attribute to our SVG to contain it
    svg.attr("viewBox", function () {
        return "" + viewBoxLeft + " " + viewBoxTop + " "  + window.innerWidth + " " + window.innerHeight;
    });

    // Adding the style attribute to our SVG to translate it
    svg.attr("style", function () {
        return "transform: translate3d(" + viewBoxLeft + "px, " + viewBoxTop + "px, 0px);";
    });
}

function update() {
    console.log("updating");
    // svg.selectAll("circle")
    //     .attr("cx", function (d) { return map.latLngToLayerPoint([d.lati, d.long]).x })
    //     .attr("cy", function (d) { return map.latLngToLayerPoint([d.lati, d.long]).y })
    translateSVG();
    // additional stuff
}

// Re-draw on reset, this keeps the markers where they should be on reset/zoom
map.on("moveend", update);
// map.on("zoomend", update);
// map.on("viewreset", update);

function calcMidpoint(x1, y1, x2, y2, bend) {
    var tmpx = (x1 + x2) / 2;
    var tmpy = (y1 + y2) / 2;
    var dx = y2 - y1;
    var dy = x1 - x2;
    var r = Math.random() / 2 + 0.05;
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

function prependAttackRow(id, args) {
    var tr = document.createElement('tr');
    count = args.length;

    for (var i = 0; i < count; i++) {
        var td = document.createElement('td');
        if (args[i] === args[2]) {
            var path = 'flags/' + args[i] + '.png';
            var img = document.createElement('img');
            img.src = path;
            td.appendChild(img);
            tr.appendChild(td);
        } else {
            var textNode = document.createTextNode(args[i]);
            td.appendChild(textNode);
            tr.appendChild(td);
        }
    }

    var element = document.getElementById(id);
    var rowCount = element.rows.length;

    // Only allow 50 rows
    if (rowCount >= 50) {
        element.deleteRow(rowCount -1);
    }

    element.insertBefore(tr, element.firstChild);
}

function prependTypeRow(id, args) {
    var tr = document.createElement('tr');
    count = args.length;

    for (var i = 0; i < count; i++) {
        var td = document.createElement('td');
        var textNode = document.createTextNode(args[i]);
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

function prependCVERow(id, args) {
    var tr = document.createElement('tr');
    tr.setAttribute("style", "height:32px;")
    //count = args.length;
    count = 1;

    for (var i = 0; i < count; i++) {

        // <th style='width:20%;'>Timestamp</th>
        // <th style='width:20%;'>Attack Type</th>
        // <th style='width:10%;'></th>
        // <th style='width:10%;'>Victim Loc</th>
        // <th style='width:10%;'></th>
        // <th style='width:10%;'>Attacker Loc</th>
        // <th style='width:20%;'>Hijacked Prefix</th>

        // var attackCve = [
        //  0   time,//msg.event_time,
        //  1   attackType,
        //  2   msg.attacker_country_code,
        //  3   msg.prefix,
        //  4   msg.attacker_country_name,
        //  5   msg.victim_country_code,
        //  6   msg.victim_country_name
        // ];
        var td1 = document.createElement('td');
        var td2 = document.createElement('td');
        var td3 = document.createElement('td');
        var td4 = document.createElement('td');
        var td5 = document.createElement('td');
        var td6 = document.createElement('td');
        var td7 = document.createElement('td');

        // Timestamp
        var textNode2 = document.createTextNode(args[0]);
        td1.appendChild(textNode2);
        tr.appendChild(td1);

        // Attack Type
        var textNode = document.createTextNode(args[1]);
        var alink = document.createElement('a');
        alink.setAttribute("href",args[1]);
        alink.setAttribute("target","_blank")
        alink.style.color = "white";
        alink.appendChild(textNode);
        td2.appendChild(alink);
        tr.appendChild(td2);

        // victim location
        var path = 'flags/' + args[2] + '.png';
        var img = document.createElement('img');
        img.src = path;
        td3.appendChild(img);
        tr.appendChild(td3);

        var textNode3 = document.createTextNode(args[4]);
        td4.appendChild(textNode3);
        tr.appendChild(td4);

        // attacker location
        var path = 'flags/' + args[5] + '.png';
        var img = document.createElement('img');
        img.src = path;
        td5.appendChild(img);
        tr.appendChild(td5);


        var textNode4 = document.createTextNode(args[6]);
        td6.appendChild(textNode4);
        tr.appendChild(td6);


        //prefix
        var textNode5 = document.createTextNode(args[3]);
        td7.appendChild(textNode5);
        tr.appendChild(td7);
        // var textNode3 = document.createTextNode(args[3]);
        // td4.appendChild(textNode3);
        // tr.appendChild(td4);
    }

    var element = document.getElementById(id);
    var rowCount = element.rows.length;

    // Only allow 50 rows
    if (rowCount >= 50) {
        element.deleteRow(rowCount -1);
    }

    element.insertBefore(tr, element.firstChild);
}

function redrawCountIP(hashID, id, countList, codeDict) {
    $(hashID).empty();
    var element = document.getElementById(id);

    // Sort ips greatest to least
    // Create items array from dict
    var items = Object.keys(countList[0]).map(function(key) {
        return [key, countList[0][key]];
    });
    // Sort the array based on the second element
    items.sort(function(first, second) {
        return second[1] - first[1];
    });
    // Create new array with only the first 50 items
    var sortedItems = items.slice(0, 50);
    var itemsLength = sortedItems.length;

    for (var i = 0; i < itemsLength; i++) {
        tr = document.createElement('tr');
        td1 = document.createElement('td');
        td2 = document.createElement('td');
        td3 = document.createElement('td');
        var key = sortedItems[i][0];
        value = sortedItems[i][1];
        var keyNode = document.createTextNode(key);
        var valueNode = document.createTextNode(value);
        var path = 'flags/' + codeDict[key] + '.png';
        var img = document.createElement('img');
        img.src = path;
        td1.appendChild(valueNode);
        td2.appendChild(img);
       
        var alink = document.createElement('a');
        alink.setAttribute("href","#");
        alink.setAttribute("class","showInfo");
        alink.style.color = "white";        
        alink.appendChild(keyNode);

        td3.appendChild(alink);
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        element.appendChild(tr);
    }
}

function redrawCountIP2(hashID, id, countList, codeDict) {
    $(hashID).empty();
    var element = document.getElementById(id);

    // Sort ips greatest to least
    // Create items array from dict
    var items = Object.keys(countList[0]).map(function(key) {
        return [key, countList[0][key]];
    });
    // Sort the array based on the second element
    items.sort(function(first, second) {
        return second[1] - first[1];
    });
    // Create new array with only the first 50 items
    var sortedItems = items.slice(0, 50);
    var itemsLength = sortedItems.length;

    for (var i = 0; i < itemsLength; i++) {
        tr = document.createElement('tr');
        td1 = document.createElement('td');
        td2 = document.createElement('td');
        td3 = document.createElement('td');
        var key = sortedItems[i][0];
        value = sortedItems[i][1];
        var keyNode = document.createTextNode(key);
        var valueNode = document.createTextNode(value);
        var path = 'flags/' + codeDict[key] + '.png';
        var img = document.createElement('img');
        img.src = path;
        td1.appendChild(valueNode);
        td2.appendChild(img);

        td3.appendChild(keyNode);
        tr.appendChild(td1);
        tr.appendChild(td2);
        tr.appendChild(td3);
        element.appendChild(tr);
    }
}

function handleLegend(msg) {
    var ipCountList = [msg.ips_tracked,
               msg.iso_code];
    var countryCountList = [msg.countries_tracked,
                msg.iso_code];
    var attackList = [msg.event_time,
              msg.src_ip,
              msg.iso_code,
              msg.country,
              msg.city,
              msg.protocol];
    redrawCountIP('#ip-tracking','ip-tracking', ipCountList, msg.ip_to_code);
    redrawCountIP2('#country-tracking', 'country-tracking', countryCountList, msg.country_to_code);
    prependAttackRow('attack-tracking', attackList);
}

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

    var attackCve = [time,//msg.event_time,
             attackType,
             msg.attacker_country_code,
             msg.prefix,
             msg.attacker_country_name,
             msg.victim_country_code,
             msg.victim_country_name
             ];

    // if (attackType != "___") {
    //     prependTypeRow('attack-type', attackType);
    // }

    if (attackCve[1] != "___"){                
        prependCVERow('attack-cveresp', attackCve);
    }
}

// WEBSOCKET STUFF
// document:https://docs.mapbox.com/mapbox.js/api/v3.3.1/l-mapbox-map/

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

    // Circle follows the line
    var dot = svg.append('circle')
        // .data({ "long": path[_index + 1][0], "lati": path[_index + 1][1] })
        .attr('r', 3)
        .attr('fill', color)
        .transition()
        // .delay(delay)
        .duration(600)
        .ease(d3.easeSin)
        .attrTween('transform', translateAlong(lineGraph.node()));

    // console.log(dot.data);

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

webSock.onmessage = function (e) {
    console.log("Got a websocket message...");
    try {
        var msg = JSON.parse(e.data);
        console.log(msg);     

        // if (msg.abnormal_path_geos.length > 0) {
        //     var attacker_geo = msg.abnormal_path_geos[0][0];
        //     var srcLatLng = new L.LatLng(attacker_geo[1], attacker_geo[0]);
        //     addCircle("#ff0000", "#ffe268", srcLatLng);
        // }

        // if (msg.normal_path_geos.length > 0) {
        //     var victim_geo = msg.normal_path_geos[0][0];
        //     var srcLatLng = new L.LatLng(victim_geo[1], victim_geo[0]);
        //     addCircle("#9ede73", "#feffde", srcLatLng);
        // }

        // var hqPoint = map.latLngToLayerPoint(hqLatLng);
        for (var i = 0; i < msg.abnormal_path_geos.length; i++) {
            transitionNext(i, 0, msg, true);
        }
        // for (var i = 0; i < msg.normal_path_geos.length; i++) {
        //     transitionNext(i, 0, msg, false);
        // }
        setTimeout(function () {
            svg.selectAll("path")
                .transition()
                .duration(1000)
                // .attr('r', circleRadius * 2.5)
                .style('opacity', 0)
                .remove();
            svg.selectAll("circle")
                .transition()
                .duration(1000)
                // .attr('r', circleRadius * 2.5)
                .style('opacity', 0)
                .remove();
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
