function partySelect(party){
    console.log('selectingparty')
    if(party=='D'){
        $('#dem_select').addClass('partyselected');
        $('#repub_select').removeClass('partyselected');
        $('#dempollgraph').css('display','block')
        $('#repubpollgraph').css('display','none')
    }
    else if (party=='R'){
        $('#repub_select').addClass('partyselected');
        $('#dem_select').removeClass('partyselected');
        $('#dempollgraph').css('display','none')
        $('#repubpollgraph').css('display','block')
    }
}

function InitChart() {
    var data = [{
        "sale": "202",
        "year": "2000"
    }, {
        "sale": "215",
        "year": "2002"
    }, {
        "sale": "179",
        "year": "2004"
    }, {
        "sale": "199",
        "year": "2006"
    }, {
        "sale": "134",
        "year": "2008"
    }, {
        "sale": "176",
        "year": "2010"
    }];
    var data2 = [{
        "sale": "152",
        "year": "2000"
    }, {
        "sale": "189",
        "year": "2002"
    }, {
        "sale": "179",
        "year": "2004"
    }, {
        "sale": "199",
        "year": "2006"
    }, {
        "sale": "134",
        "year": "2008"
    }, {
        "sale": "176",
        "year": "2010"
    }];
    var vis = d3.select(".currentpolls"),
        WIDTH = 600,
        HEIGHT = 400,
        MARGINS = {
            top: 20,
            right: 20,
            bottom: 20,
            left: 50
        },
        xScale = d3.scale.linear().range([MARGINS.left, WIDTH - MARGINS.right]).domain([2000, 2010]),
        yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([134, 215]),
        xAxis = d3.svg.axis()
        .scale(xScale),
        yAxis = d3.svg.axis()
        .scale(yScale)
        .orient("left");
    
    vis.append("svg:g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
        .call(xAxis);
    vis.append("svg:g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + (MARGINS.left) + ",0)")
        .call(yAxis);
    var lineGen = d3.svg.line()
        .x(function(d) {
            return xScale(d.year);
        })
        .y(function(d) {
            return yScale(d.sale);
        })
        .interpolate("basis");
    vis.append('svg:path')
        .attr('d', lineGen(data))
        .attr('stroke', 'green')
        .attr('stroke-width', 2)
        .attr('fill', 'none');
    vis.append('svg:path')
        .attr('d', lineGen(data2))
        .attr('stroke', 'blue')
        .attr('stroke-width', 2)
        .attr('fill', 'none');
}

function pullData(route,dataname){
    $.post(route, {dataname:dataname}, function(data){handleData(data,dataname)});
}

function organizedDownload(){
    input = $('#dataref').val().split(',')
    i = input.length - 1
    while (i > 0){
        pullData(input[0],input[i])
        i --;
    }
}

function handleData(data,dataname){
    console.log(dataname)
    //console.log(data)
}


// A $( document ).ready() block.
$( document ).ready(function() {
    console.log( "ready!" );
    InitChart();
    organizedDownload();
    partySelect('D');
});
