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



function pullData(route,dataname){
    $.post(route, {dataname:dataname}, function(data){handleData(data,dataname)});
}

function organizedDownload(){
    input = $('#dataref').val().split(',')
    for (i=input.length - 1;i > 0;i--){
        pullData(input[0],input[i])
    }
}

//helper function for parseVar
function validateLine(line,index){
    var ret = 0
    date = new Date(line[0])
    pos = parseInt(line[index])
    if(pos >= 0){
        ret = [date,pos]
    }
    return ret
}

function parseVar(data, index){
    var polldata = {pollarray:[]};
    for(i=1;i<data.length;i++){
        line = data[i].split(',')
        validated = validateLine(line,index)
        if(validated != 0){
            polldata.pollarray.push({
                "date" : validated[0],
                "position" : validated[1],
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
    edomain = new Date(datarows[1].split(',')[0].split(' ')[0])
    sdomain = new Date(datarows[datarows.length - 2].split(',')[0].split(' ')[0])
    domain = [sdomain,edomain]
    initChart(parseddata,dataname,domain)
}

function initChart(dataarray,svgid,domain) {

    var vis = d3.select('#'+svgid),
        WIDTH = 600,
        HEIGHT = 350,
        MARGINS = {
            top: 50,
            right: 50,
            bottom: 50,
            left: 50
        },
        xScale = d3.time.scale().range([MARGINS.left, WIDTH - MARGINS.right]).domain([domain[0],domain[1]]),
        yScale = d3.scale.linear().range([HEIGHT - MARGINS.top, MARGINS.bottom]).domain([0, 100]),
        xAxis = d3.svg.axis().scale(xScale).ticks(10).tickFormat(d3.time.format("%b %Y")),
        yAxis = d3.svg.axis().scale(yScale).orient("left");
    
    vis.append("svg:g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (HEIGHT - MARGINS.bottom) + ")")
        .call(xAxis)
        .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)")
    vis.append("svg:g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + (MARGINS.left) + ",0)")
        .call(yAxis);
    var lineGen = d3.svg.line()
        .x(function(d) {
            return xScale(d.date);
        })
        .y(function(d) {
            return yScale(d.position);
        })
        .interpolate("basis");

    for(i=0;i<dataarray.length;i++){
        vis.append('svg:path')
            .attr('d', lineGen(dataarray[i]))
            .attr('stroke', 'red')
            .attr('stroke-width', 2)
            .attr('fill', 'none');
    }
}


//on page load
$( document ).ready(function() {
    organizedDownload();
    partySelect('D');
});

//on window resize (makes the svgs responsive)
$(window).on("resize", function() {
  var targetWidth = $('.visual').width();
  the_chart.attr("width", targetWidth);
  the_chart.attr("height", Math.round(targetWidth / aspect));
}).trigger("resize");
