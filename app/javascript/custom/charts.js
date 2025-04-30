document.getElementById("plots").addEventListener("turbo:frame-render", function (event) {
  if (typeof(chart_json_data) !== undefined) {
    show_plot(chart_json_data, "highcharts_plot");
  }
  if (typeof(chart_datetime_title) !== undefined) {
    titleChart(chart_datetime_title);
  }
})

function show_plot(jsonData, targetDiv){
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
  var axisLineWidth = 1;
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

  new Highcharts.Chart({
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
    xAxis: {
      type: 'datetime',
      title: {
        text: json_panels.panels_arr[0].xtitle || 'Time'
      }
    },
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
        gridZIndex: 1
      }
    ],
    // data
    series: series,
  });
}

function titleChart(titleText) {

  var title_chart = new Highcharts.Chart({
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