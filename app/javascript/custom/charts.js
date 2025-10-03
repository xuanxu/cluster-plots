// ECharts-based charting implementation for Cluster Plots
// Converted from Highcharts to Apache ECharts

var visibility_crossline = 0;
window.visibility_crossline = visibility_crossline;
var title_chart, axis_chart, plot_charts;
var all_charts = {};

document.getElementById("plots").addEventListener("turbo:frame-render", function (event) {
  if (typeof(status_processing_data) !== "undefined" && status_processing_data === 'error') {
    set_current_zoom("");
    status_processing_data = "";
  } else {
    process_plots_data();
  }
});

function process_plots_data(){
  if (typeof(chart_json_data) !== "undefined") {
    show_plots(chart_json_data);
  }
  if (typeof(chart_start_datetime) !== "undefined") {
    titleChart(chart_start_datetime + "/" + chart_stop_datetime);
    set_plot_times(chart_start_datetime, chart_stop_datetime);
    set_current_zoom(chart_start_datetime + " " + chart_stop_datetime);
  }
}

function show_plots(jsonData){
  all_charts = {}
  window.all_charts = {title: undefined, axis: undefined, plot_charts: [], spacecraft: undefined};
  const json_panels = JSON.parse(jsonData);

  set_cef_files_list(json_panels.list_cef);

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
    var option = plot.getOption();
    var xAxis = option.xAxis[0];
    var axis_start_datetime = xAxis.min;
    var axis_stop_datetime = xAxis.max;
    axisChart(axis_start_datetime, axis_stop_datetime)
  }

  return plot;
}

// Helper function to format datetime for ECharts
function formatDateTime(timestamp) {
  return echarts.format.formatTime('yyyy-MM-dd\nHH:mm:ss', timestamp);
}

// Helper function to format date for timestamp recording
function formatDateForRecord(timestamp) {
  const date = new Date(timestamp);
  return date.toISOString().replace('.000Z', 'Z');
}

function plot_line(plot_data, nplot){
  var json = plot_data.subpanels[0];
  var panel_type = plot_data.panel_type;

  var yrange = json.yrange_caa;
  var subTop = 100 - json.size;
  var sub_height = json.size;

  const default_line_thickness = 2;
  const font_size = 11;

  // custom ticks ?
  var flag_ticks = json.ytickflag;
  var tick_val = json.ytickval;
  var tick_txt = json.yticktxt;

  var num_lines = json.plot.length;
  var series = [];
  
  for (var l = 0; l < num_lines; l++) {
    var line_thickness = default_line_thickness;
    if  (panel_type === 'status') {
      line_thickness =  json.plot[l].thick;
    }

    var display_legend = true;
    if (json.plot[l].legend === 0) {
      display_legend = false;
    }
    var name = json.plot[l].name;

    var symbol = 'circle';
    var symbol_size = line_thickness;
    var line_width = line_thickness;
    var show_symbol = false;
    
    if (json.plot[l].type === 'scatter') {
      symbol = 'diamond';
      symbol_size = 6;
      line_width = 0;
      show_symbol = true;
    }

    // Convert data points - ensure numbers not strings
    const convertedData = json.plot[l].data.map(point => {
      if (Array.isArray(point)) {
        return [
          typeof point[0] === 'string' ? Number(point[0]) : point[0],
          typeof point[1] === 'string' ? Number(point[1]) : point[1]
        ];
      }
      return point;
    });

    var serie = {
      name: name,
      type: json.plot[l].type === 'scatter' ? 'scatter' : 'line',
      data: convertedData,
      color: json.plot[l].color,
      lineStyle: {
        width: line_width,
        color: json.plot[l].color
      },
      symbol: symbol,
      symbolSize: symbol_size,
      showSymbol: show_symbol,
      animation: false
    };

    series.push(serie);
  }

  var container = document.getElementById('chart_plot_' + nplot);
  container.style.height = '250px';
  var chart = echarts.init(container);
  
  var option = {
    backgroundColor: 'white',
    grid: {
      left: 120,
      right: 120,
      top: subTop + '%',
      bottom: 10,
      height: sub_height + '%',
      show: true,
      borderColor: '#CBD6EA',
      borderWidth: 2
    },
    xAxis: {
      type: 'time',
      axisLine: {
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      axisTick: {
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        },
        length: 5
      },
      minorTick: {
        show: true,
        splitNumber: 5,
        lineStyle: {
          color: '#CBD6EA',
          width: 1
        },
        length: 2
      },
      axisLabel: {
        show: false,
        fontSize: 12
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#ADD8E6',
          width: 1
        }
      },
      minorSplitLine: {
        show: true,
        lineStyle: {
          color: '#E6F2F2',
          width: 1
        }
      }
    },
    yAxis: {
      type: json.ytype === 'logarithmic' ? 'log' : 'value',
      min: yrange[0],
      max: yrange[1],
      name: json.ytitle,
      nameLocation: 'middle',
      nameGap: json.rotate === 0 ? 80 : 60,
      nameTextStyle: {
        fontSize: font_size,
        fontWeight: 'normal'
      },
      nameRotate: json.rotate,
      axisLine: {
        show: true,
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      axisTick: {
        show: true,
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      minorTick: {
        show: true,
        splitNumber: 5,
        lineStyle: {
          color: '#CBD6EA',
          width: 1
        }
      },
      axisLabel: {
        fontSize: font_size,
        formatter: function(value) {
          if (flag_ticks === 1 && tick_val) {
            var idx = tick_val.findIndex(v => Math.abs(v - value) < 0.0001);
            if (idx >= 0 && tick_txt && tick_txt[idx]) {
              return tick_txt[idx];
            }
          }
          return value;
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#E6F2F2',
          width: 1
        }
      },
      minorSplitLine: {
        show: true,
        lineStyle: {
          color: '#F5F5F5',
          width: 1
        }
      }
    },
    series: series,
    legend: {
      show: true,
      orient: 'vertical',
      right: 10,
      top: 'middle',
      textStyle: {
        fontSize: font_size
      }
    },
    tooltip: {
      trigger: 'none'
    },
    animation: false
  };

  // Add Y=0 line if needed
  if (json.ytype !== 'logarithmic' && yrange[0] <= 0 && yrange[1] >= 0) {
    option.yAxis.axisLine.onZeroAxisIndex = 0;
  }

  chart.setOption(option);
  
  // Add plot label
  chart.setOption({
    graphic: [{
      type: 'text',
      right: 10,
      top: 5,
      style: {
        text: plot_data.label,
        fontSize: 11,
        fill: '#222',
        backgroundColor: 'rgba(255,255,255,0.8)',
        padding: [5, 8],
        borderColor: 'silver',
        borderWidth: 2,
        borderRadius: 5
      },
      z: 100
    }]
  });

  // Add zoom and click handlers
  chart.on('click', function(params) {
    if (params.componentType === 'series') {
      record_timestamp(formatDateForRecord(params.data[0]));
    } else if (params.componentType === 'xAxis') {
      record_timestamp(formatDateForRecord(params.value));
    }
  });

  chart.getZr().on('mousedown', function(params) {
    chart._brushStartX = params.offsetX;
  });

  chart.getZr().on('mouseup', function(params) {
    if (chart._brushStartX !== undefined) {
      var endX = params.offsetX;
      var startX = chart._brushStartX;
      
      if (Math.abs(endX - startX) > 5) {
        var xAxis = chart.getModel().getComponent('xAxis', 0);
        var coordSys = chart.getModel().getSeriesByIndex(0).coordinateSystem;
        
        var startTime = coordSys.getAxis('x').coordToData(Math.min(startX, endX));
        var endTime = coordSys.getAxis('x').coordToData(Math.max(startX, endX));
        
        var start_selection = formatDateForRecord(startTime);
        var stop_selection = formatDateForRecord(endTime);
        document.getElementById("zoom_to").value = start_selection + " " + stop_selection;
        window.dispatchEvent(new CustomEvent("zoom_in"));
      }
      
      delete chart._brushStartX;
    }
  });

  // Store chart instance
  chart._nplot = nplot;
  chart._container = container;
  
  // Add methods for compatibility with existing code
  chart.xAxis = [{
    getExtremes: function() {
      var option = chart.getOption();
      return {
        min: option.xAxis[0].min || option.series[0].data[0][0],
        max: option.xAxis[0].max || option.series[0].data[option.series[0].data.length-1][0]
      };
    },
    update: function(options) {
      chart.setOption({
        xAxis: options
      });
    },
    tickPositions: []
  }];
  
  chart.yAxis = [{
    setExtremes: function(min, max, redraw) {
      chart.setOption({
        yAxis: {
          min: min,
          max: max
        }
      });
    },
    getExtremes: function() {
      var option = chart.getOption();
      return {
        min: option.yAxis[0].min,
        max: option.yAxis[0].max
      };
    },
    update: function(options, redraw) {
      chart.setOption({
        yAxis: options
      });
    },
    setTitle: function(options) {
      chart.setOption({
        yAxis: {
          name: options.text
        }
      });
    },
    addPlotLine: function(options) {
      var currentOption = chart.getOption();
      var markLines = currentOption.yAxis[0].axisPointer?.value ? [currentOption.yAxis[0].axisPointer] : [];
      markLines.push({
        value: options.value,
        lineStyle: {
          color: options.color || 'red',
          width: options.width || 1,
          type: options.dashStyle === 'ShortDash' ? 'dashed' : 'solid'
        },
        label: {
          show: false
        }
      });
      chart.setOption({
        series: chart.getOption().series.map((s, idx) => {
          if (idx === 0) {
            return {
              markLine: {
                silent: true,
                symbol: 'none',
                data: markLines.map(ml => ({yAxis: ml.value, lineStyle: ml.lineStyle}))
              }
            };
          }
          return {};
        })
      });
      chart._plotLines = chart._plotLines || {};
      chart._plotLines[options.id] = options;
    },
    removePlotLine: function(id) {
      if (chart._plotLines && chart._plotLines[id]) {
        delete chart._plotLines[id];
        var remainingLines = Object.values(chart._plotLines);
        chart.setOption({
          series: chart.getOption().series.map((s, idx) => {
            if (idx === 0) {
              return {
                markLine: {
                  silent: true,
                  symbol: 'none',
                  data: remainingLines.map(ml => ({yAxis: ml.value, lineStyle: ml.lineStyle || {}}))
                }
              };
            }
            return {};
          })
        });
      }
    }
  }, {
    // Second y-axis (opposite side)
    setExtremes: function(min, max, redraw) {
      // Same as first axis in ECharts
      chart.yAxis[0].setExtremes(min, max, redraw);
    },
    update: function(options, redraw) {
      chart.yAxis[0].update(options, redraw);
    }
  }];
  
  chart.redraw = function() {
    // ECharts handles redraw automatically
  };
  
  // Add series property with forEach support for line thickness updates
  chart.series = chart.getOption().series.map((s, idx) => ({
    type: s.type,
    update: function(options) {
      var currentSeries = chart.getOption().series;
      currentSeries[idx] = Object.assign(currentSeries[idx], options);
      chart.setOption({
        series: currentSeries
      });
    }
  }));

  return chart;
} // plot_line

function plot_heatmap(plot_data, nplot){
  var json = plot_data.subpanels[0];
  var zrange = json.zrange;
  var ymin = json.yrange[0];
  var ymax = json.yrange[1];
  var yrange = json.yrange;
  var yrange_plot = json.yrange_caa;

  var subTop = 100 - json.size;
  var sub_height = json.size;

  const font_size = 11;
  const default_line_thickness = 2;

  var series = [];
  var num_lines = json.plot.length;
  
  for (var l = 0; l < num_lines; l++) {
    var convertedData = json.plot[l].data.map(point => {
      if (Array.isArray(point)) {
        return [
          typeof point[0] === 'string' ? Number(point[0]) : point[0],
          typeof point[1] === 'string' ? Number(point[1]) : point[1],
          typeof point[2] === 'string' ? Number(point[2]) : point[2],
        ];
      }
      return point;
    });

    if (json.plot[l].type === 'line') {
      var line = {
        type: 'line',
        name: json.plot[l].name,
        data: convertedData.map(p => [p[0], p[1]]),
        color: json.plot[l].color,
        lineStyle: {
          width: default_line_thickness,
          color: json.plot[l].color
        },
        symbol: 'circle',
        symbolSize: json.plot[l].thick / 2.,
        showSymbol: false,
        animation: false
      };
      series.push(line);
    } else {
      var heatmap = {
        type: 'heatmap',
        data: convertedData,
        animation: false
      };
      series.push(heatmap);
    }
  }

  var container = document.getElementById('chart_plot_' + nplot);
  container.style.height = '250px';
  var chart = echarts.init(container);

  // Define color stops for heatmap
  var visualMapPieces = [];
  if (json.ztype === 'logarithmic') {
    var logMin = Math.log10(zrange[0]);
    var logMax = Math.log10(zrange[1]);
    var stops = [0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1];
    var colors = ['#000000', '#0000ff', '#007FFF', '#00ffff', '#7FFF7F', '#ffff00', '#FF7F00', '#ff0000', '#7F0000'];
    
    for (var i = 0; i < stops.length - 1; i++) {
      var minVal = Math.pow(10, logMin + stops[i] * (logMax - logMin));
      var maxVal = Math.pow(10, logMin + stops[i + 1] * (logMax - logMin));
      visualMapPieces.push({
        min: minVal,
        max: maxVal,
        color: colors[i]
      });
    }
  }
  
  var option = {
    backgroundColor: 'white',
    grid: {
      left: 120,
      right: 120,
      top: subTop + '%',
      bottom: 10,
      height: sub_height + '%',
      show: true,
      borderColor: '#CBD6EA',
      borderWidth: 2
    },
    xAxis: {
      type: 'time',
      axisLine: {
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      axisTick: {
        show: true,
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        },
        length: 5
      },
      minorTick: {
        show: true,
        splitNumber: 5,
        lineStyle: {
          color: '#CBD6EA',
          width: 1
        },
        length: 2
      },
      axisLabel: {
        show: true,
        fontSize: 12,
        formatter: function(value) {
          return echarts.format.formatTime('HH:mm:ss', value);
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#ADD8E6',
          width: 1
        }
      }
    },
    yAxis: {
      type: json.ytype === 'logarithmic' ? 'log' : 'value',
      min: yrange_plot[0],
      max: yrange_plot[1],
      name: json.ytitle,
      nameLocation: 'middle',
      nameGap: 60,
      nameTextStyle: {
        fontSize: font_size
      },
      axisLine: {
        show: false,
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      axisTick: {
        show: false
      },
      axisLabel: {
        show: false
      },
      splitLine: {
        show: false
      }
    },
    series: series,
    visualMap: {
      type: json.ztype === 'logarithmic' ? 'piecewise' : 'continuous',
      min: zrange[0],
      max: zrange[1],
      calculable: false,
      orient: 'vertical',
      right: 10,
      top: 'middle',
      text: [json.ztitle, ''],
      textStyle: {
        fontSize: font_size
      },
      inRange: {
        color: ['#000000', '#0000ff', '#007FFF', '#00ffff', '#7FFF7F', '#ffff00', '#FF7F00', '#ff0000', '#7F0000']
      },
      pieces: visualMapPieces.length > 0 ? visualMapPieces : undefined,
      formatter: function(value) {
        if (json.ztype === 'logarithmic') {
          return value.toExponential(1);
        }
        return value;
      }
    },
    tooltip: {
      trigger: 'none'
    },
    animation: false
  };

  chart.setOption(option);
  
  // Add plot label
  chart.setOption({
    graphic: [{
      type: 'text',
      right: 10,
      top: 5,
      style: {
        text: plot_data.label,
        fontSize: 11,
        fill: '#222',
        backgroundColor: 'rgba(255,255,255,0.8)',
        padding: [5, 8],
        borderColor: 'silver',
        borderWidth: 2,
        borderRadius: 5
      },
      z: 100
    }]
  });

  // Add zoom handlers
  chart.on('click', function(params) {
    if (params.componentType === 'xAxis') {
      record_timestamp(formatDateForRecord(params.value));
    }
  });

  chart.getZr().on('mousedown', function(params) {
    chart._brushStartX = params.offsetX;
  });

  chart.getZr().on('mouseup', function(params) {
    if (chart._brushStartX !== undefined) {
      var endX = params.offsetX;
      var startX = chart._brushStartX;
      
      if (Math.abs(endX - startX) > 5) {
        var coordSys = chart.getModel().getSeriesByIndex(0).coordinateSystem;
        
        var startTime = coordSys.getAxis('x').coordToData(Math.min(startX, endX));
        var endTime = coordSys.getAxis('x').coordToData(Math.max(startX, endX));
        
        var start_selection = formatDateForRecord(startTime);
        var stop_selection = formatDateForRecord(endTime);
        document.getElementById("zoom_to").value = start_selection + " " + stop_selection;
        window.dispatchEvent(new CustomEvent("zoom_in"));
      }
      
      delete chart._brushStartX;
    }
  });

  // Store chart instance
  chart._nplot = nplot;
  chart._container = container;
  
  // Add methods for compatibility
  chart.yAxis = [{
    setExtremes: function(min, max, redraw) {
      chart.setOption({
        yAxis: {
          min: min,
          max: max
        }
      });
    },
    getExtremes: function() {
      var option = chart.getOption();
      return {
        min: option.yAxis[0].min,
        max: option.yAxis[0].max
      };
    },
    update: function(options, redraw) {
      chart.setOption({
        yAxis: options
      });
    },
    setTitle: function(options) {
      chart.setOption({
        yAxis: {
          name: options.text
        }
      });
    }
  }, {
    setExtremes: function(min, max, redraw) {
      chart.yAxis[0].setExtremes(min, max, redraw);
    },
    update: function(options, redraw) {
      chart.yAxis[0].update(options, redraw);
    }
  }];
  
  chart.xAxis = [{
    update: function(options) {
      chart.setOption({
        xAxis: options
      });
    }
  }];
  
  chart.colorAxis = [{
    update: function(options) {
      chart.setOption({
        visualMap: {
          min: options.min,
          max: options.max
        }
      });
    }
  }];
  
  chart.zoomOut = function() {
    // No-op for now
  };
  
  chart.redraw = function() {
    // No-op, ECharts handles this automatically
  };
  
  // Add series property with forEach support
  chart.series = chart.getOption().series.map((s, idx) => ({
    type: s.type,
    update: function(options) {
      var currentSeries = chart.getOption().series;
      currentSeries[idx] = Object.assign(currentSeries[idx], options);
      chart.setOption({
        series: currentSeries
      });
    }
  }));

  return chart;
} // plot_heatmap
window.plot_heatmap = plot_heatmap;

function add_subpanels(plot, plot_data, nplot) {
  // ECharts doesn't support multiple y-axes in the same way as Highcharts
  // This would need significant restructuring
  // For now, we'll skip this complex feature
  console.warn('Subpanels not yet fully supported in ECharts migration');
} // add_subpanels

function titleChart(titleText) {
  var container = document.getElementById('title-chart');
  title_chart = echarts.init(container);
  
  var option = {
    title: {
      text: titleText,
      left: 'center',
      top: 10,
      textStyle: {
        fontWeight: 'bold',
        fontSize: 14
      }
    },
    xAxis: { show: false },
    yAxis: { show: false },
    series: []
  };
  
  title_chart.setOption(option);
  
  // Add compatibility wrapper for Highcharts API
  title_chart.options = {
    title: {
      get text() {
        var opt = title_chart.getOption();
        return opt.title && opt.title[0] ? opt.title[0].text : '';
      },
      set text(value) {
        title_chart.setOption({
          title: {
            text: value
          }
        });
      }
    }
  };
  
  all_charts["title"] = title_chart;
}

function axisChart(start, stop) {
  var container = document.getElementById('axis-chart');
  axis_chart = echarts.init(container);
  
  var option = {
    grid: {
      left: 120,
      right: 120,
      top: 0,
      bottom: 40
    },
    xAxis: {
      type: 'time',
      min: start,
      max: stop,
      axisLine: {
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      axisTick: {
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        },
        length: 5
      },
      minorTick: {
        show: true,
        splitNumber: 5,
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        },
        length: 2
      },
      axisLabel: {
        fontSize: 12,
        formatter: function(value) {
          return echarts.format.formatTime('HH:mm:ss', value);
        }
      },
      splitLine: {
        show: false
      }
    },
    yAxis: {
      show: false
    },
    series: []
  };
  
  axis_chart.setOption(option);
  
  // Add compatibility wrapper for Highcharts API
  axis_chart.xAxis = [{
    get min() {
      var opt = axis_chart.getOption();
      return opt.xAxis && opt.xAxis[0] ? opt.xAxis[0].min : start;
    },
    get max() {
      var opt = axis_chart.getOption();
      return opt.xAxis && opt.xAxis[0] ? opt.xAxis[0].max : stop;
    },
    tickPositions: [],
    update: function(options) {
      axis_chart.setOption({
        xAxis: options
      });
    }
  }];
  
  all_charts["axis"] = axis_chart;
}

// Synchronized crosshairs for ECharts
function syncronizeCrossHairs(chart) {
  // Simplified crosshair implementation
  chart.getZr().on('mousemove', function(e) {
    if (window.visibility_crossline === 1) {
      var pointInGrid = [e.offsetX, e.offsetY];
      var coordSys = chart.getModel().getSeriesByIndex(0).coordinateSystem;
      if (coordSys) {
        var xValue = coordSys.getAxis('x').coordToData(pointInGrid[0]);
        
        // Update all charts with crossline
        var syncronized_charts = window.all_charts["plot_charts"];
        if (window.all_charts["axis"]) {
          syncronized_charts = syncronized_charts.concat([window.all_charts["axis"]]);
        }
        
        syncronized_charts.forEach(function(c, i) {
          if (c && c.setOption) {
            c.setOption({
              xAxis: {
                axisPointer: {
                  show: true,
                  value: xValue,
                  lineStyle: {
                    color: 'red',
                    width: 1
                  }
                }
              }
            });
          }
        });
      }
    }
  });
}

function zoom_in_selection(event) {
  // Handled in individual chart click handlers
}

/* EXPORTING FUNCTIONALITY */
// ECharts has built-in export functionality
window.exportChartsToImage = async function(format, filename) {
  try {
    const charts = window.all_charts["plot_charts"];
    const canvases = [];
    
    // Get all chart canvases
    for (let i = 0; i < charts.length; i++) {
      if (charts[i]) {
        const url = charts[i].getDataURL({
          type: format === 'image/png' ? 'png' : format === 'image/jpeg' ? 'jpeg' : 'png',
          pixelRatio: 2,
          backgroundColor: '#fff'
        });
        canvases.push(url);
      }
    }
    
    // For now, download the first chart
    // A complete implementation would combine all charts
    if (canvases.length > 0) {
      const link = document.createElement('a');
      link.download = filename || 'chart.' + (format === 'image/png' ? 'png' : 'jpg');
      link.href = canvases[0];
      link.click();
    }
  } catch (e) {
    console.error('Failed to export charts:', e);
  }
};

/**
 * Create ECharts chart to plot spacecraft information
 */
window.plot_spacecraft_info = function(json_data, spacecraft_id, mission_id, info_list, min_x_value, max_x_value) {
  var data = [];
  var spacecraft_label = [];

  var spacecraft_colors = {
    "C1": "black",
    "C2": "red",
    "C3": "LimeGreen",
    "C4": "blue",
    "D1": "navy",
    "D2": "magenta"
  };

  var spacecraft_name = "";
  if (mission_id === 1) {
    spacecraft_name = "C" + spacecraft_id;
  } else {
    spacecraft_name = "D" + spacecraft_id;
  }

  var spacecraft_color = spacecraft_colors[spacecraft_name];
  
  for (var i = 0; i < json_data.sc_info[0].data.length; i++) {
    var timestamp = Date.parse(json_data.sc_info[0].data[i]);
    data.push([timestamp, null]);
  }

  var container = document.getElementById('spacecraft-info');
  container.style.height = '200px';
  var spacecraft_info_chart = echarts.init(container);
  
  // Build title text
  var titleLines = [spacecraft_name];
  for (var s = 0; s < json_data.sc_info.length-1; s++) {
    titleLines.push(json_data.sc_info[s + 1].name);
  }
  
  var option = {
    grid: {
      left: 120,
      right: 120,
      bottom: 435
    },
    title: {
      text: titleLines.join('\n'),
      left: 60,
      top: 0,
      textStyle: {
        fontSize: 11,
        color: spacecraft_color,
        fontWeight: 'bold',
        lineHeight: 14
      }
    },
    xAxis: {
      type: 'time',
      min: min_x_value,
      max: max_x_value,
      axisLine: {
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      axisTick: {
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      minorTick: {
        show: true,
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        }
      },
      axisLabel: {
        fontSize: 11,
        formatter: function(value, index) {
          // Show spacecraft info at specific points
          var lab = '';
          for (var s = 0; s < json_data.sc_info.length-1; s++) {
            var val = json_data.sc_info[s+1].data[index];
            lab += (val === null ? '-' : Number(val).toFixed(1)) + '\n';
          }
          return lab || '';
        }
      }
    },
    yAxis: {
      show: false
    },
    series: [{
      type: 'line',
      data: data,
      color: 'black',
      symbol: 'none'
    }]
  };
  
  spacecraft_info_chart.setOption(option);
  window.all_charts["spacecraft"] = spacecraft_info_chart;

  return spacecraft_info_chart;
}
