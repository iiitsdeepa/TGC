function partySelect(party){
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

function initChart(dataarray,svgid,domain) {
    console.log(svgid)
    domains = domain.split(',')
    console.log(domains[0])
    console.log(domains[1])
    var vis = d3.select('#'+svgid),
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
        .attr('d', lineGen(dataarray[0]))
        .attr('stroke', 'green')
        .attr('stroke-width', 2)
        .attr('fill', 'none');
    vis.append('svg:path')
        .attr('d', lineGen(dataarray[1]))
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

function parseVar(data, index){
    var polldata = {pollarray:[]};
    for(i=1;i<data.length;i++){
        line = data[i].split(',')
        if(line[index] != '-1'){
            polldata.pollarray.push({
                "position" : parseInt(line[index]),
                "date" : line[0]
            });
        }
    }
    return (polldata.pollarray)
}

function handleData(data,dataname){
    datarows = data.split('\n');
    column_names = datarows[0].split(',');
    var parseddata = new Array()
    for(j=1;j<column_names.length;j++){
        parseddata[j-1] = parseVar(datarows,j)
    }
    edomain = datarows[1].split(',')[0]
    sdomain = datarows[datarows.length - 2].split(',')[0]
    domain = sdomain+','+edomain
    initChart(parseddata,dataname,domain)
}


// A $( document ).ready() block.
$( document ).ready(function() {
    console.log( "ready!" );
    organizedDownload();
    partySelect('D');
});
