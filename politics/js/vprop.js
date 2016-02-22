function partySelect(party){
    if(party=='D'){
        $('#dem_select').addClass('partyselected');
        $('#repub_select').removeClass('partyselected');
        $('#dem_national').css('display','block')
        $('#repub_national').css('display','none')
    }
    else if (party=='R'){
        $('#repub_select').addClass('partyselected');
        $('#dem_select').removeClass('partyselected');
        $('#dem_national').css('display','none')
        $('#repub_national').css('display','block')
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
    var margin = {top: 20, right: 20, bottom: 50, left: 20}
    width = 600 - margin.left - margin.right;
    height = 400 - margin.top - margin.bottom;
    
    var xScale = d3.time.scale().range([margin.left, width - margin.right]).domain([domain[0],domain[1]]);
    var yScale = d3.scale.linear().range([height - margin.top, margin.bottom]).domain([0, 100]);

    var chart = d3.select('#'+svgid)
        .append('svg:svg')
        .attr('width', width + margin.right + margin.left)
        .attr('height', height + margin.top + margin.bottom)
        .attr('id', svgid+'_chart')
        .attr('class', 'chart')
        .attr('viewBox', '0 0 600 400');

    var main = chart.append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        .attr('width', width)
        .attr('height', height)
        .attr('class', 'main');

    var xAxis = d3.svg.axis().scale(xScale).ticks(10).tickFormat(d3.time.format("%b %Y"));
    var yAxis = d3.svg.axis().scale(yScale).orient("left");
    
    main.append('g')
        .attr('transform', 'translate(0,' + (height - margin.bottom) + ')')
        .attr('class', 'x axis')
        .call(xAxis)
        .selectAll("text")
            .style("text-anchor", "end")
            .attr("dx", "-.8em")
            .attr("dy", ".15em")
            .attr("transform", "rotate(-65)");

    main.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(" + (margin.left) + ","+(margin.top-margin.bottom)+")")
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
        main.append('g:path')
            .attr("transform", "translate(0,"+(margin.top-margin.bottom)+")")
            .attr('d', lineGen(dataarray[i]))
            .attr('stroke', 'red')
            .attr('stroke-width', 2)
            .attr('fill', 'none');
    }
    var targetWidth = $('.visual').width();
    $('.chart').attr("width", targetWidth);
}


//on page load
$( document ).ready(function(){
    //organizedDownload();
    partySelect('D');
});


//on window resize (makes the svgs responsive)
$(window).on("resize", function() {
  var targetWidth = $('.visual').width();
  $('.chart').attr("width", targetWidth);
}).trigger("resize");
