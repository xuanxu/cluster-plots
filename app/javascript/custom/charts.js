var title_chart, axis_chart;

document.getElementById("plots").addEventListener("turbo:frame-render", function (event) {
  if (typeof(chart_json_data) !== undefined) {
    show_plot(chart_json_data, "highcharts_plot");
  }
  if (typeof(chart_start_datetime) !== undefined) {
    titleChart( chart_start_datetime + "/" + chart_stop_datetime);
  }
})

function show_plot(jsonData, targetDiv){
  setHighchartsGlobalSettings();

  const json_panels = JSON.parse(jsonData);
  const json = json_panels.panels_arr[0].subpanels[0];
  const default_line_thickness = 2;
  const font_size = '11px';

  var sub_height = json.size + '%';
  // custom ticks ?
  var flag_ticks = json.ytickflag;
  var tick_val = undefined;
  if (flag_ticks == 1) {
    tick_val = json.ytickval;
  }

  var yoffset = 60;
  var ywidth = undefined;
  if (json.rotate == 0) {
    yoffset = 80;
    ywidth = 150;
  }
  var subTop = 100 - json.size;
  var axisLineWidth = 2;
  var axisTickWidth = 2;

  var majorGridDisplay = 1;
  var minorGridDisplay = 1;
  var yrange = json.yrange_caa;

  if (json.type == 'line') {
    var num_lines = json.plot.length;
    var series = [];
    for (var l = 0; l < num_lines; l++) {
      var line_thickness = default_line_thickness;
      if  (json_panels.panels_arr[0].panel_type == 'status') {
        line_thickness =  json.plot[l].thick;
      }

      var display_legend = true;
      if (json.plot[l].legend == 0) {
        display_legend = false;
      }
      var name = json.plot[l].name;

      var symbol = 'circle';
      var radius = line_thickness/2.;
      var line_width = line_thickness;
      var enabled = undefined;
      var marker_line_width = 0;
      if (json.plot[l].type == 'scatter') {
        symbol = 'cross';
        radius = 3;
        line_width = 0;
        marker_line_width = 2;
        enabled = true;
      }

      // Convert data points - ensure numbers not strings
      const convertedData = json.plot[l].data.map(point => {
        if (Array.isArray(point)) {
          return [
            // Convert timestamp to number if it's a string
            typeof point[0] === 'string' ? parseFloat(point[0]) : point[0],
            // Convert value to number if it's a string
            typeof point[1] === 'string' ? parseFloat(point[1]) : point[1]
          ];
        }
        return point;
      });

      var line = {
        name: name,
        type: json.plot[l].type,
        showInLegend: display_legend,
        color: json.plot[l].color,
        lineWidth: line_width,
        data: convertedData,
        marker: {
          enabled: enabled,
          symbol:  symbol,
          radius:  radius,
          lineColor: null,
          lineWidth: marker_line_width
        }
      }

      series.push(line);
    }
  }

  var line_plot = new Highcharts.Chart({
    title: { text: "" },
    chart: {
      type: 'line',
      renderTo: targetDiv,
      zoomType: 'x',
      events:{
        selection: function (event) {
          return zoom(event,div);
        },
        // Add the plot label (eg: C1 EFW)
        load: function () {
          var label = this.renderer.label(json_panels.panels_arr[0].label)
          .css({
            width: '80px',
            color: '#222',
            fontSize: '11px'
          })
          .attr({
            'stroke': 'silver',
            'stroke-width': 2,
            'r': 5,
            'padding': 10
          })
          .add();
            label.align(Highcharts.extend(label.getBBox(), {
              align: 'right',
              verticalAlign: 'top',
              y: -5,
              x: -7
            }), null, 'spacingBox');
        }
      }
    },
    xAxis: [
      {
        type: 'datetime',
        title: {
          enable: false,
        },
        labels: { enabled: false },
        startOnTick: false,
        endOnTick: false,
        minPadding: 0,
        maxPadding: 0,
        lineWidth: 2,
        tickLength: 5,
        tickWidth: 2,
        minorTickLength: 2,
        minorTickWidth: 1,
        minorTickInterval: 'auto',
        gridLineWidth: 1,
        gridLineColor: '#ADD8E6',
        lineColor: '#CBD6EA',
        tickColor: '#CBD6EA',
        minorTickColor: '#CBD6EA'
      },
      {
        type: 'datetime',
        opposite: true,
        linkedTo: 0,
        title: { enabled: false },
        labels: { enabled: false },
        startOnTick: false,
        endOnTick: false,
        minPadding: 0,
        maxPadding: 0,
        lineWidth: axisLineWidth,
        tickLength: 5,
        tickWidth: 2,
        minorTickLength: 2,
        minorTickWidth: 1,
        gridLineWidth: 0,
        lineColor: '#CBD6EA',
        tickColor: '#CBD6EA',
        minorTickColor: '#CBD6EA'
      }
    ],
    yAxis: [
      {
        title: {
          enabled: true,
          rotation: json.rotate,
          offset: yoffset,
          style :{
            fontSize: font_size,
            width: ywidth
          },
          text: json.ytitle
        },
        tickPositions: tick_val,
        labels: {
          style: { fontSize: font_size },
          formatter: function () {
            var label = this.axis.defaultLabelFormatter.call(this);
            if (flag_ticks == 1) {
              tickvalues = json.ytickval;
              ticknames = json.yticktxt;
              idx = tickvalues.findIndex(tic => tic === this.value);
              return ticknames[idx];
            } else {
              return label;
            }
          }
        },
        plotLines: [{
          color: '#A9A9A9',
          width: 2,
          value: 0,
          dashStyle: 'ShortDash'
        }],
        height: sub_height,
        top: subTop + '%',
        offset: 0,
        minPadding: 0,
        maxPadding: 0,
        min: yrange[0],
        max: yrange[1],
        startOnTick: false,
        endOnTick: false,
        lineWidth: axisLineWidth,
        tickWidth: axisTickWidth,
        type: json.ytype,
        minorTicks: true,
        minorTicksLength: 5,
        minorTickWidth: 1,
        gridLineWidth: majorGridDisplay,
        minorGridLineWidth: minorGridDisplay,
        lineColor: '#CBD6EA',
        tickColor: '#CBD6EA',
        minorTickColor: '#CBD6EA'
      },
      { // axis on the opposite side to "close" the box
        title: { enabled: false },
        opposite: true,
        labels: { enabled: false },
        height: sub_height,
        top: subTop + '%',
        offset: 0,
        minPadding: 0,
        maxPadding: 0,
        min: yrange[0],
        max: yrange[1],
        startOnTick: false,
        endOnTick: false,
        lineWidth: axisLineWidth,
        tickWidth: axisTickWidth,
        type: json.ytype,
        minorTicks: true,
        minorTicksLength: 5,
        minorTickWidth: 1,
        gridLineWidth: majorGridDisplay,
        minorGridLineWidth: minorGridDisplay,
        gridZIndex: 1,
        lineColor: '#CBD6EA',
        tickColor: '#CBD6EA',
        minorTickColor: '#CBD6EA'
      }
    ],
    // data
    series: series,
  });

  var axis_start_datetime = line_plot.xAxis[0].getExtremes().min;
  var axis_stop_datetime = line_plot.xAxis[0].getExtremes().max;
  axisChart(axis_start_datetime, axis_stop_datetime)
}

function titleChart(titleText) {
  title_chart = new Highcharts.Chart({
    chart: {
      renderTo: "title-chart"
    },
    exporting: {
      sourceWidth: 1000,
      sourceHeight: 50
    },
    title:{
      text: titleText,
      enabled: true,
      y: 20,
      style: {
        fontWeight: 'bold'
      }
    }
  });
}

function axisChart(start,stop) {
  axis_chart = new Highcharts.Chart({
    title: { enabled: false, text: "" },
    chart: {
      renderTo: 'axis-chart',
      height: 50,
      marginBottom: 40,
      marginTop: 0,
    },
    exporting: {
      sourceWidth: 1000,
      sourceHeight: 40
    },
    yAxis: [{
      showEmpty: true,
      title: { enabled: false }
    }],
    xAxis: [{
      type: 'datetime',
      min: start,
      max: stop,
      showEmpty: true,
      gridLineWidth: 0,
      minorGridLineWidth: 0,
      labels: {
        enabled: true,
        style: {
          fontSize: '12px',
        },
        formatter: function () {
          return Highcharts.dateFormat('%H:%M:%S', this.value);
        }
      },
      lineWidth: 2,
      tickWidth: 2,
      tickLength: 5,
      minorTickLength: 2,
      minorTickWidth: 2,
      minorTickInterval: 'auto',
      lineColor: '#CBD6EA',
      tickColor: '#CBD6EA',
      minorTickColor: '#CBD6EA'
    }]
  });

  window["axis_chart"] = axis_chart;
  var line = {
    color: 'black',
    data: [],
    showInLegend: false
  }
  axis_chart.addSeries(line, false);
  axis_chart.redraw();
}

function setHighchartsGlobalSettings(){
  Highcharts.setOptions({
    global: {
      time: { useUTC: true }
    },
    chart: {
      backgroundColor:'white',
      borderColor: '#003399',
      borderWidth: 0,
      margin: [10, 120, 10, 120],
      height: 250,
      // hide highcharts default 'reset zoom' button
      resetZoomButton: {
        theme: { display: 'none' }
      },
    },
    title: {
      enabled: false,
      text: ''
    },
    exporting: {
      allowHTML: true,
      sourceWidth: 1000,
      sourceHeight: 300,
      fallbackToExportServer: false, // Ensure the export happens on the client side or not at all
      buttons: {
        contextButton: {
          enabled: false // hide default highcharts download button
        }
      }
    },
    credits: {
      enabled: false
    },
    legend: {
      layout: 'vertical',
      reversed: true,
      borderWidth: 0,
      floating: true,
      align: 'right',
      verticalAlign: 'middle',
      x: -5,
      y: 10
    },
    labels: {
      align: 'right',
      x: -10,
      y: 0
    },
    tooltip: { enabled: false },
    plotOptions: {
      enableMouseTracking: false,
      series: {
        states: {
          inactive: { opacity: 1 }, // to cancel serie highlight on mouse hover need to set opacity to 1
          hover: { enabled: false  },//disable any styling of a currently hovered line series => don't want the markers to be highlighted when hovering on the line
         }
      },
    },
    series: []
  });
}