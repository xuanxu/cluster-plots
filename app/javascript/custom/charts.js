var visibility_crossline = 0
window.visibility_crossline = visibility_crossline;
var title_chart, axis_chart, plot_charts;
var all_charts = {};

document.getElementById("plots").addEventListener("turbo:frame-render", function (event) {
  if (typeof(chart_json_data) !== "undefined") {
    show_plots(chart_json_data);
  }
  if (typeof(chart_start_datetime) !== "undefined") {
    titleChart( chart_start_datetime + "/" + chart_stop_datetime);
  }
})

function show_plots(jsonData){
  window.all_charts = {title: undefined, axis: undefined, plot_charts: []};
  setHighchartsGlobalSettings();
  const json_panels = JSON.parse(jsonData);

  plot_charts = [];
  for (var nplot = 0 ; nplot < json_panels.panels_arr.length ; nplot++) {
    var plot_data = json_panels.panels_arr[nplot];
    plot_charts.push(create_plot(plot_data, nplot));
  }
  all_charts["plot_charts"] = plot_charts;
  window.all_charts = all_charts;
}

function create_plot(plot_data, nplot){
  var plot = undefined;

  var plot_type = plot_data.panel_type;
  if (plot_type === 'line') {
    plot = plot_line(plot_data, nplot);
  } else if (plot_type === 'spectrogram') {
    plot = plot_heatmap(plot_data, nplot);
  } else if (plot_type === 'status') {
    plot = plot_line(plot_data, nplot);
    add_subpanels(plot, plot_data, nplot);
  }

  if (nplot === 0 && plot !== undefined) {
    var axis_start_datetime = plot.xAxis[0].getExtremes().min;
    var axis_stop_datetime = plot.xAxis[0].getExtremes().max;
    axisChart(axis_start_datetime, axis_stop_datetime)
  }

  return plot;
}

function plot_line(plot_data, nplot){
  var plot = undefined;
  var json = plot_data.subpanels[0];
  var panel_type = plot_data.panel_type;

  var yrange = json.yrange_caa;

  var subTop = 100 - json.size;
  var sub_height = json.size + '%';

  var axisLineWidth = 2;
  var axisTickWidth = 2;

  var majorGridDisplay = 1;
  var minorGridDisplay = 1;

  const default_line_thickness = 2;
  const font_size = '11px';

  // custom ticks ?
  var flag_ticks = json.ytickflag;
  var tick_val = undefined;
  if (flag_ticks == 1) { tick_val = json.ytickval; }

  var yoffset = 60;
  var ywidth = undefined;
  if (json.rotate == 0) {
    yoffset = 80;
    ywidth = 150;
  }

  var num_lines = json.plot.length;
  var series = [];
  for (var l = 0; l < num_lines; l++) {
    var line_thickness = default_line_thickness;
    if  (panel_type === 'status') {
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
    if (json.plot[l].type === 'scatter') {
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

  plot = new Highcharts.Chart({
    title: { text: "" },
    chart: {
      type: 'line',
      renderTo: 'highcharts_plot_' + nplot,
      events:{
        // Add the plot label (eg: C1 EFW)
        load: function () {
          var label = this.renderer.label(plot_data.label)
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
        minorTickColor: '#CBD6EA',
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
              var tickvalues = json.ytickval;
              var ticknames = json.yticktxt;
              var idx = tickvalues.findIndex(tic => tic === this.value);
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
        tickPositions: tick_val,
        opposite: true,
        linkedTo: 0,
        labels: { enabled: false },
        height: sub_height,
        top: subTop + '%',
        startOnTick: false,
        endOnTick: false,
        lineWidth: axisLineWidth,
        tickWidth: axisTickWidth,
        type: json.ytype,
        minorTicks: true,
        minorTicksLength: 5,
        minorTickWidth: 1,
        lineColor: '#CBD6EA',
        tickColor: '#CBD6EA',
        minorTickColor: '#CBD6EA'
      }
    ],
    // data
    series: series,
  },
  function(chart) {
    syncronizeCrossHairs(chart);
  });

  plot.yAxis[0].setExtremes(yrange[0],yrange[1],false);
  plot.yAxis[1].setExtremes(yrange[0],yrange[1],true);

  return plot;
} // plot_line

function plot_heatmap(plot_data, nplot){
  var plot = undefined;
  var json = plot_data.subpanels[0];
	// define range to use
  var zrange = json.zrange;
  var ymin = json.yrange[0];
  var ymax = json.yrange[1];

  var yrange = json.yrange;
  var yrange_plot = json.yrange_caa;

  var subTop = 100 - json.size;
  var sub_height = json.size + '%';

  var axisLineWidth = 2;
  var axisTickWidth = 2;

  var majorGridDisplay = 1;
  var minorGridDisplay = 1;

  const font_size = '11px';
  const default_line_thickness = 2;

  var series = [];
  var num_lines = json.plot.length;
  for (var l = 0; l < num_lines; l++) {
    var data = [];

    var convertedData = json.plot[l].data.map(point => {
      if (Array.isArray(point)) {
        return [
          // Convert timestamp to number if it's a string
          typeof point[0] === 'string' ? parseFloat(point[0]) : point[0],
          // Convert values to numbers if they are a string
          typeof point[1] === 'string' ? parseFloat(point[1]) : point[1],
          typeof point[2] === 'string' ? parseFloat(point[2]) : point[2],
        ];
      }
      return point;
    });

    if (json.plot[l].type === 'line') {
      var line_thickness = default_line_thickness;

      var line = {
        type: 'line',
        name: json.plot[l].name,
        color: json.plot[l].color,
        lineWidth: line_thickness,
        data: convertedData,
        marker: {
            symbol: 'circle',
            radius: json.plot[l].thick/2.
        }
      }
      series.push(line);
    } else {
      var heatmap = {
        type: 'heatmap',
        pointPlacement: 'on', // properly align tickmarks
        colsize: json.delta_x,
        rowsize: json.delta_y,
        data: convertedData,
        boostThreshold: 0
      }
      series.push(heatmap);
    }
  }

  plot = new Highcharts.Chart({
    title: { text: "" },
    chart: {
      renderTo: 'highcharts_plot_' + nplot,
      type: 'heatmap',
      events:{
      // Add the plot label (eg: C1 EFW)
        load: function () {
          var label = this.renderer.label(plot_data.label)
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
    xAxis: [{
      type: 'datetime',
      title: {
        enable: false,
      },
      //labels: { enabled: false },
      labels: {
        enabled: true,
        style: {
          fontSize: '12px',
        },
        formatter: function () {
          return Highcharts.dateFormat('%H:%M:%S', this.value);
        }
      },
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
      minorTickColor: '#CBD6EA',
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
    }],
    yAxis: [{
      top: subTop + '%',
      height: sub_height,
      minPadding: 0,
      maxPadding: 0,
      startOnTick: false,
      endOnTick: false,
      tickWidth: 0,
      lineWidth: 0,
      min: yrange_plot[0],
      max: yrange_plot[1],
      minorGridLineWidth: 0,
      gridLineColor: 'transparent',
      title: {
        // unit for the colorbar
        enabled: true,
        margin: 100,
        text: json.ztitle
      },
      labels: {
        enabled: false
      },
      type: 'linear',
      minorTickLength: 0,
      tickLength: 0,
      opposite: true
    },{
      // visible axis
      id: 'yAxis.HeatmapGrouping',
      type: json.ytype,
      min: yrange[0],
      max: yrange[1],
      title: {
        enabled: true,
        offset: 60,
        style :{ fontSize: font_size },
        text: json.ytitle
      },
      labels: {
        style :{ fontSize: font_size }
      },
      top: subTop + '%',
      height: sub_height,
      minPadding: 0,
      maxPadding: 0,
      startOnTick: false,
      endOnTick: false,
      lineWidth: axisLineWidth,
      tickWidth: axisTickWidth,
      minorTicks: true,
      minorTickLength: 5,
      minorTickWidth: 1,
      gridLineWidth: majorGridDisplay,
      minorGridLineWidth: minorGridDisplay,
      lineColor: '#CBD6EA',
      tickColor: '#CBD6EA',
      minorTickColor: '#CBD6EA'
    }],
    legend: { // placement of the color bar
      align: 'right',
      layout: 'vertical',
      margin: 0,
      verticalAlign: 'top',
      y: 35,
      x: -30,
      symbolHeight: 170 // height of the colorbar
    },
    colorAxis: {
      stops: [
        [0, '#000000'],		// lower than min range
        [0.125, '#0000ff'],
        [0.25, '#007FFF'],
        [0.375, '#00ffff'],
        [0.5, '#7FFF7F'],
        [0.625, '#ffff00'],
        [0.75, '#FF7F00'],
        [0.875, '#ff0000'],
        [1, '#7F0000']		// higher than max range
      ],
      type: json.ztype,
      min: zrange[0],
      max: zrange[1],
      reversed: false,
      startOnTick: false,
      endOnTick: false,
      minorTickWidth: 1,
      minorTickInterval: 0.1,
      tickColor: '#000000',
      tickWidth: 1,
      // don't extend the graduations across the colorAxis
      minorGridLineWidth: 0,
      gridLineWidth: 0,
      marker: null, // tooltip on the colorbar
      labels: {
      style :{ fontSize: font_size },
      x: 7,
      //format: '{value}'
      formatter: function(){
        if (json.ztype === 'logarithmic') {
          return (this.value).toExponential(1);
        } else {
          return this.value;
        }
      }
    }
    },
    // data
    series: series,
  },
  function(chart) {
    syncronizeCrossHairs(chart);
  }
  );

  // somehow putting the grid display values directly
  // in the axis definition seems to shift the first/last value of the heatmap ?!?
  plot.yAxis[0].update({ gridLineWidth: majorGridDisplay,  minorGridLineWidth:minorGridDisplay });
  plot.yAxis[1].update({ gridLineWidth: majorGridDisplay, minorGridLineWidth:minorGridDisplay });

  plot.yAxis[0].setExtremes(yrange[0],yrange[1],false);
  plot.yAxis[1].setExtremes(yrange[0],yrange[1],true);

  plot.zoomOut();
  plot.redraw();

  return plot;
} // plot_heatmap

function add_subpanels(plot, plot_data, nplot) {
  var subTop = 100 - plot_data.subpanels[0].size;
  const font_size = '11px';
  var axis_labels = {};

  for (var subpanel_index = 1; subpanel_index < plot_data.subpanels.length; subpanel_index++) {
    var subpanel_json = plot_data.subpanels[subpanel_index];

    var sub_height = subpanel_json.size - 2 + '%';
	  var num_lines = subpanel_json.plot.length;
    subTop = subTop - subpanel_json.size;
    var bck_color = '#FFFAFA';
    if ( plot.yAxis.length % 4 === 0 ) { bck_color = 'white'; }

    var tick_values = undefined;
    var flag_ticks = subpanel_json.ytickflag;
    if (flag_ticks == 1) {
      tick_values = subpanel_json.ytickval;
      var left_yAxis_index = subpanel_index * 2
      axis_labels[left_yAxis_index] = subpanel_json.yticktxt;
    }

    var yoffset = 60;
    var ywidth = undefined;
    if (subpanel_json.rotate == 0) {
      yoffset = 80;
      ywidth = 150;
    }

    var axisLineWidth = 2;
    var axisTickWidth = 2;

    plot.addAxis({
      id: 'subpanel_yAxis.' + subpanel_index,
		  title: {
        enabled: true,
		    rotation: subpanel_json.rotate,
        offset: yoffset,
        style :{
				  fontSize: font_size,
				  width: ywidth
		    },
        text: subpanel_json.ytitle
      },
      tickPositions: tick_values,
      labels: {
        style :{ fontSize: font_size },
        formatter: function () {
          if (flag_ticks == 1) {
            var idx = tick_values.findIndex(tic => tic === this.value);
            return axis_labels[this.axis.index][idx];
          } else {
            return this.axis.defaultLabelFormatter.call(this);
          }
        }
      },
      plotBands: [{
        from: subpanel_json.yrange_caa[0],
        to: subpanel_json.yrange_caa[1],
        color: bck_color,
        zIndex: 0
      }],
      height: sub_height,
      top: subTop + '%',
      offset: 0,
      minPadding: 0,
      maxPadding: 0,
      min: subpanel_json.yrange_caa[0],
      max: subpanel_json.yrange_caa[1],
      startOnTick: false,
      endOnTick: false,
      lineWidth: 2,
      tickWidth: 2,
      type: subpanel_json.ytype,
      minorTicks: true,
      minorTicksLength: 10,
      minorTickWidth: 1,
      gridLineWidth: 1,
      minorGridLineWidth: 1,
      lineColor: '#CBD6EA',
      tickColor: '#CBD6EA',
      minorTickColor: '#CBD6EA',
	  });

    var new_axis_index = plot.yAxis.length - 1;
    // axis on the opposite side to close the box
    plot.addAxis({
      id: 'subpanel_yAxis_opposite.' + subpanel_index,
      linkedTo: new_axis_index,
      opposite: true,
      title: { enabled: false },
      labels: { enabled: false },
      plotLines: [{
        value: subpanel_json.yrange_caa[0],
        width: 1,
        color: '#6D9EEB',
        zIndex: 4
      },{
        value: subpanel_json.yrange_caa[1],
        width: 1,
        color: '#6D9EEB',
        zIndex: 4
      }],
      height: sub_height,
      top: subTop + '%',
      offset: 0,
      minPadding: 0,
      maxPadding: 0,
      min: subpanel_json.yrange_caa[0],
      max: subpanel_json.yrange_caa[1],
      startOnTick: false,
      endOnTick: false,
      lineWidth: axisLineWidth,
      tickWidth: axisTickWidth,
      type: subpanel_json.ytype,
      minorTicks: true,
      minorTicksLength: 10,
      minorTickWidth: 1,
      gridLineWidth: 0,
      minorGridLineWidth: 0,
      lineColor: '#CBD6EA',
      tickColor: '#CBD6EA',
      minorTickColor: '#CBD6EA'
    });

    for (var l = 0; l < num_lines; l++) {
      var display_legend = true;
      var line_plot_info = subpanel_json.plot[l];
      var line_name = line_plot_info.name
      if (subpanel_json.plot[l].legend == 0) {
        display_legend = false;
      } else if (l === 0) {
        line_name += '<br/> ... <br/>';
      }

      // Convert data points - ensure numbers not strings
      const convertedData = line_plot_info.data.map(point => {
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
        name: line_name,
        showInLegend: display_legend,
        color: line_plot_info.color,
        lineWidth: line_plot_info.thick,
        data: convertedData,
		    yAxis: new_axis_index,
        marker: {
          enabled: undefined,
          symbol: 'circle',
          radius: line_plot_info.thick / 2.,
          lineWidth: 0,
          lineColor: null,
        }
      }
      plot.addSeries(line,false);
    }
  }
  plot.redraw();
} // add_subpanels

function titleChart(titleText) {
  title_chart = new Highcharts.Chart({
    chart: {
      renderTo: "title-chart",
      events: { click: undefined },
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
  all_charts["title"] = title_chart;
}

function axisChart(start, stop) {
  axis_chart = new Highcharts.Chart({
    title: { enabled: false, text: "" },
    chart: {
      renderTo: 'axis-chart',
      height: 50,
      marginBottom: 40,
      marginTop: 0,
      events: { click: undefined },
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
  },
  function(chart) {
    syncronizeCrossHairs(chart);
  });

  var line = {
    color: 'black',
    data: [],
    showInLegend: false
  }
  axis_chart.addSeries(line, false);
  axis_chart.redraw();

  all_charts["axis"] = axis_chart;
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
      events: {
        click: function (event) {
          record_timestamp(Highcharts.dateFormat( "%Y-%m-%dT%H:%M:%SZ",event.xAxis[0].value));
        }
      }
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
      y: 10,
      navigation: { enabled: false } // disable legend navigation
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
          hover: { enabled: false  }, // disable any styling of a currently hovered line series => don't want the markers to be highlighted when hovering on the line
        },
        events: {
          // save time value of the nearest point when clicking on the serie
          click: function (event) {
            record_timestamp(Highcharts.dateFormat( "%Y-%m-%dT%H:%M:%SZ",event.point.x));
          }
        }
      }
    },
    series: []
  });

  // Plot heatmaps in canvas instead of SVG
  // to improve performance with large datasets
  (function (H) {
    var Series = H.Series,
        each = H.each;

    /**
     * Create a hidden canvas to draw the graph on. The contents is later copied over
     * to an SVG image element.
     */
    Series.prototype.getContext = function () {
      if (!this.canvas) {
        this.canvas = document.createElement('canvas');
        this.canvas.setAttribute('width', this.chart.chartWidth);
        this.canvas.setAttribute('height', this.chart.chartHeight);
        this.image = this.chart.renderer.image('', 0, 0, this.chart.chartWidth, this.chart.chartHeight).add(this.group);
        this.ctx = this.canvas.getContext('2d');
      }
      return this.ctx;
    };

    /**
     * Draw the canvas image inside an SVG image
     */
    Series.prototype.canvasToSVG = function () {
      this.image.attr({ href: this.canvas.toDataURL('image/png') });
    };

    /**
     * Wrap the drawPoints method to draw the points in canvas instead of the slower SVG,
     * that requires one shape each point.
     */
    H.wrap(H.seriesTypes.heatmap.prototype, 'drawPoints', function () {
      var ctx = this.getContext();
      if (ctx) {
        // draw the columns
        this.points.forEach(function (point) {
          var plotY = point.plotY,
            shapeArgs,
            pointAttr;

          if (plotY !== undefined && !isNaN(plotY) && point.y !== null) {
            shapeArgs = point.shapeArgs;
            pointAttr = (point.pointAttr && point.pointAttr['']) || point.series.pointAttribs(point);
            ctx.fillStyle = pointAttr.fill;
            ctx.fillRect(shapeArgs.x, shapeArgs.y, shapeArgs.width, shapeArgs.height);
          }
        });
        this.canvasToSVG();
      } else {
        this.chart.showLoading('Your browser doesn\'t support HTML5 canvas, <br>please use a modern browser');
      }
    });
    H.seriesTypes.heatmap.prototype.directTouch = false; // Use k-d-tree
  }(Highcharts));


  Highcharts.Legend.prototype.update = function (options) {
    this.options = Highcharts.merge(this.options, options);
    this.chart.isDirtyLegend = true;
    this.chart.isDirtyBox = true;
    this.chart.redraw();
  };
}

// Add synchronized vertical line at mouse position
function syncronizeCrossHairs(chart) {
  var container = chart.container;

  container.addEventListener('mousemove', function(e) {
    var syncronized_charts = window.all_charts["plot_charts"].concat(window.all_charts["axis"]);
    var num_plots = syncronized_charts.length;
    var x = e.clientX - chart.plotLeft - container.offsetLeft;
    var xAxis = chart.xAxis[0];

    for (var i = 0; i < num_plots; i++) {
      //remove old plot line and draw new plot line (crosshair) for this chart
      var chart_xAxis = syncronized_charts[i].xAxis[0];
      chart_xAxis.removePlotLine("custom_crossline_" + i);
      if (window.visibility_crossline === 1) {
        chart_xAxis.addPlotLine({
          value: chart.xAxis[0].translate(x, true),
          width: 1,
          color: 'red',
          id: "custom_crossline_" + i,
          zIndex: 10   // or won't appear on heatmap
        });
      }
    }
  });
}

function record_timestamp(x){
  alert(x);
}
