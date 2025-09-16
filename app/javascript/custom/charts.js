var visibility_crossline = 0
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
  setEchartsGlobalSettings();
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
    var xAxis = plot.getOption().xAxis[0];
    var axis_start_datetime = xAxis.min || Date.parse(chart_start_datetime);
    var axis_stop_datetime = xAxis.max || Date.parse(chart_stop_datetime);
    axisChart(axis_start_datetime, axis_stop_datetime)
  }

  return plot;
}

function plot_line(plot_data, nplot){
  var json = plot_data.subpanels[0];
  var panel_type = plot_data.panel_type;

  var yrange = json.yrange_caa;
  var num_lines = json.plot.length;
  
  // Create series data for Echarts
  var series = [];
  for (var l = 0; l < num_lines; l++) {
    var line_thickness = panel_type === 'status' ? json.plot[l].thick : 2;
    var display_legend = json.plot[l].legend !== 0;
    var name = json.plot[l].name;
    
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

    var seriesItem = {
      name: name,
      type: json.plot[l].type === 'scatter' ? 'scatter' : 'line',
      data: convertedData,
      itemStyle: {
        color: json.plot[l].color
      },
      lineStyle: {
        width: json.plot[l].type === 'scatter' ? 0 : line_thickness,
        color: json.plot[l].color
      },
      symbol: json.plot[l].type === 'scatter' ? 'cross' : 'circle',
      symbolSize: json.plot[l].type === 'scatter' ? 6 : line_thickness,
      showSymbol: json.plot[l].type === 'scatter',
      smooth: false
    };
    
    if (!display_legend) {
      seriesItem.showInLegend = false;
    }
    
    series.push(seriesItem);
  }

  // Create Echarts option
  var option = {
    animation: false,
    title: {
      text: '',
      show: false
    },
    grid: {
      left: 120,
      right: 120,
      top: 10,
      bottom: 10,
      containLabel: false
    },
    legend: {
      type: 'scroll',
      orient: 'vertical',
      right: 5,
      top: 'middle',
      show: true
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
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
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#ADD8E6',
          width: 1
        }
      },
      axisLabel: {
        show: false
      }
    },
    yAxis: {
      type: json.ytype === 'logarithmic' ? 'log' : 'value',
      name: json.ytitle,
      nameLocation: 'middle',
      nameGap: 80,
      nameTextStyle: {
        fontSize: 11,
        fontWeight: 'normal'
      },
      min: yrange[0],
      max: yrange[1],
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
      splitLine: {
        lineStyle: {
          color: '#f0f0f0',
          width: 1
        }
      },
      axisLabel: {
        fontSize: 11,
        formatter: function(value) {
          if (json.ytickflag === 1) {
            var idx = json.ytickval.findIndex(tic => tic === value);
            return idx >= 0 ? json.yticktxt[idx] : value;
          }
          return value;
        }
      }
    },
    series: series,
    toolbox: {
      show: false
    },
    tooltip: {
      show: false
    },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
        filterMode: 'none'
      }
    ]
  };

  // Custom ticks handling
  if (json.ytickflag === 1) {
    option.yAxis.interval = 1;
    option.yAxis.min = Math.min(...json.ytickval);
    option.yAxis.max = Math.max(...json.ytickval);
  }

  // Create chart instance
  var chart = echarts.init(document.getElementById('echarts_plot_' + nplot));
  
  // Add plot label
  setTimeout(() => {
    const labelDiv = document.createElement('div');
    labelDiv.style.cssText = `
      position: absolute;
      top: 5px;
      right: 15px;
      padding: 10px;
      background: white;
      border: 2px solid silver;
      border-radius: 5px;
      font-size: 11px;
      color: #222;
      z-index: 1000;
      pointer-events: none;
    `;
    labelDiv.textContent = plot_data.label;
    chart.getDom().parentElement.style.position = 'relative';
    chart.getDom().parentElement.appendChild(labelDiv);
  }, 100);

  chart.setOption(option);
  
  // Setup event handlers for zoom and crosshairs
  setupChartEvents(chart, nplot);
  
  return chart;
}

function setupChartEvents(chart, nplot) {
  // Handle brush/zoom selection
  chart.on('brush', function(params) {
    if (params.areas && params.areas.length > 0) {
      var area = params.areas[0];
      var startTime = area.coordRange[0];
      var endTime = area.coordRange[1];
      
      var start_selection = new Date(startTime).toISOString().replace('.000Z', 'Z');
      var stop_selection = new Date(endTime).toISOString().replace('.000Z', 'Z');
      
      document.getElementById("zoom_to").value = start_selection + " " + stop_selection;
      window.dispatchEvent(new CustomEvent("zoom_in"));
    }
  });

  // Handle click events for timestamp recording
  chart.on('click', function(params) {
    if (params.value && params.value[0]) {
      var timestamp = new Date(params.value[0]).toISOString().replace('.000Z', 'Z');
      record_timestamp(timestamp);
    }
  });

  // Setup mouse events for crosshairs
  setupCrosshairs(chart);

  return chart;
}

function setupCrosshairs(chart) {
  chart.getDom().addEventListener('mousemove', function(e) {
    if (window.visibility_crossline === 1) {
      var rect = chart.getDom().getBoundingClientRect();
      var x = e.clientX - rect.left;
      var point = chart.convertFromPixel('grid', [x, 0]);
      
      if (point && point[0]) {
        // Update crosshairs for all charts
        var syncronized_charts = window.all_charts["plot_charts"].concat(window.all_charts["axis"] ? [window.all_charts["axis"]] : []);
        
        syncronized_charts.forEach(function(syncChart) {
          if (syncChart && syncChart.setOption) {
            syncChart.setOption({
              graphic: [{
                type: 'line',
                shape: {
                  x1: x, y1: 0,
                  x2: x, y2: syncChart.getHeight()
                },
                style: {
                  stroke: 'red',
                  lineWidth: 1
                },
                z: 1000
              }]
            });
          }
        });
      }
    }
  });
}

function plot_heatmap(plot_data, nplot){
  var json = plot_data.subpanels[0];
  var zrange = json.zrange;
  var yrange = json.yrange;
  
  var series = [];
  var num_lines = json.plot.length;
  
  for (var l = 0; l < num_lines; l++) {
    var convertedData = json.plot[l].data.map(point => {
      if (Array.isArray(point)) {
        return [
          typeof point[0] === 'string' ? Number(point[0]) : point[0],
          typeof point[1] === 'string' ? Number(point[1]) : point[1],
          typeof point[2] === 'string' ? Number(point[2]) : point[2]
        ];
      }
      return point;
    });

    if (json.plot[l].type === 'line') {
      var lineSeriesItem = {
        type: 'line',
        name: json.plot[l].name,
        data: convertedData.map(point => [point[0], point[1]]),
        itemStyle: {
          color: json.plot[l].color
        },
        lineStyle: {
          width: 2,
          color: json.plot[l].color
        },
        symbol: 'circle',
        symbolSize: json.plot[l].thick,
        showSymbol: true
      };
      series.push(lineSeriesItem);
    } else {
      // Heatmap data
      var heatmapSeriesItem = {
        type: 'heatmap',
        data: convertedData,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      };
      series.push(heatmapSeriesItem);
    }
  }

  var option = {
    animation: false,
    title: {
      text: '',
      show: false
    },
    grid: {
      left: 120,
      right: 150,
      top: 10,
      bottom: 50,
      containLabel: false
    },
    xAxis: {
      type: 'time',
      boundaryGap: false,
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
        }
      },
      splitLine: {
        show: true,
        lineStyle: {
          color: '#ADD8E6',
          width: 1
        }
      },
      axisLabel: {
        show: true,
        fontSize: 12,
        formatter: function(value) {
          return echarts.format.formatTime('hh:mm:ss', value);
        }
      }
    },
    yAxis: {
      type: json.ytype === 'logarithmic' ? 'log' : 'value',
      name: json.ytitle,
      nameLocation: 'middle',
      nameGap: 80,
      nameTextStyle: {
        fontSize: 11
      },
      min: yrange[0],
      max: yrange[1],
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
      splitLine: {
        lineStyle: {
          color: '#f0f0f0',
          width: 1
        }
      },
      axisLabel: {
        fontSize: 11
      }
    },
    visualMap: {
      min: zrange[0],
      max: zrange[1],
      calculable: true,
      orient: 'vertical',
      right: 30,
      top: 35,
      itemHeight: 170,
      inRange: {
        color: ['#000000', '#0000ff', '#007FFF', '#00ffff', '#7FFF7F', '#ffff00', '#FF7F00', '#ff0000', '#7F0000']
      },
      text: ['High', 'Low'],
      textStyle: {
        fontSize: 11
      }
    },
    series: series,
    toolbox: {
      show: false
    },
    tooltip: {
      show: false
    },
    dataZoom: [
      {
        type: 'inside',
        xAxisIndex: 0,
        filterMode: 'none'
      }
    ]
  };

  var chart = echarts.init(document.getElementById('echarts_plot_' + nplot));
  
  // Add plot label
  setTimeout(() => {
    const labelDiv = document.createElement('div');
    labelDiv.style.cssText = `
      position: absolute;
      top: 5px;
      right: 15px;
      padding: 10px;
      background: white;
      border: 2px solid silver;
      border-radius: 5px;
      font-size: 11px;
      color: #222;
      z-index: 1000;
      pointer-events: none;
    `;
    labelDiv.textContent = plot_data.label;
    chart.getDom().parentElement.style.position = 'relative';
    chart.getDom().parentElement.appendChild(labelDiv);
  }, 100);

  chart.setOption(option);
  setupChartEvents(chart, nplot);
  
  return chart;
}

function add_subpanels(plot, plot_data, nplot) {
  // For Echarts, we'll need to handle subpanels differently
  // This is a complex feature that would require significant refactoring
  // For now, we'll implement a basic version
  
  for (var subpanel_index = 1; subpanel_index < plot_data.subpanels.length; subpanel_index++) {
    var subpanel_json = plot_data.subpanels[subpanel_index];
    var num_lines = subpanel_json.plot.length;
    
    for (var l = 0; l < num_lines; l++) {
      var line_plot_info = subpanel_json.plot[l];
      var display_legend = line_plot_info.legend !== 0;
      var line_name = line_plot_info.name;
      
      if (l === 0 && display_legend) {
        line_name += '\n ... \n';
      }

      const convertedData = line_plot_info.data.map(point => {
        if (Array.isArray(point)) {
          return [
            typeof point[0] === 'string' ? Number(point[0]) : point[0],
            typeof point[1] === 'string' ? Number(point[1]) : point[1]
          ];
        }
        return point;
      });

      var seriesItem = {
        name: line_name,
        type: 'line',
        data: convertedData,
        itemStyle: {
          color: line_plot_info.color
        },
        lineStyle: {
          width: line_plot_info.thick,
          color: line_plot_info.color
        },
        symbol: 'circle',
        symbolSize: line_plot_info.thick / 2,
        showSymbol: false,
        yAxisIndex: subpanel_index
      };
      
      // Add the new series to the existing chart
      var currentOption = plot.getOption();
      currentOption.series.push(seriesItem);
      
      // We would need to add a new yAxis for each subpanel
      // This is a simplified implementation
      plot.setOption(currentOption);
    }
  }
}

function titleChart(titleText) {
  var option = {
    title: {
      text: titleText,
      left: 'center',
      top: 'middle',
      textStyle: {
        fontWeight: 'bold',
        fontSize: 14
      }
    },
    grid: {
      show: false
    },
    xAxis: {
      show: false
    },
    yAxis: {
      show: false
    }
  };

  title_chart = echarts.init(document.getElementById('title-chart'));
  title_chart.setOption(option);
  title_chart.resize({height: 50});
  
  all_charts["title"] = title_chart;
}

function axisChart(start, stop) {
  var option = {
    animation: false,
    grid: {
      left: 120,
      right: 120,
      top: 0,
      bottom: 40,
      containLabel: false
    },
    xAxis: {
      type: 'time',
      min: start,
      max: stop,
      boundaryGap: false,
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
        splitNumber: 2,
        lineStyle: {
          color: '#CBD6EA',
          width: 2
        },
        length: 2
      },
      splitLine: {
        show: false
      },
      axisLabel: {
        show: true,
        fontSize: 12,
        formatter: function(value) {
          return echarts.format.formatTime('hh:mm:ss', value);
        }
      }
    },
    yAxis: {
      show: false
    },
    series: [{
      type: 'line',
      data: [],
      showSymbol: false,
      lineStyle: {
        opacity: 0
      }
    }]
  };

  axis_chart = echarts.init(document.getElementById('axis-chart'));
  axis_chart.setOption(option);
  axis_chart.resize({height: 50});
  
  setupCrosshairs(axis_chart);
  all_charts["axis"] = axis_chart;
}

function setEchartsGlobalSettings(){
  // Set global Echarts configuration
  window.echartsGlobalConfig = {
    backgroundColor: 'white',
    animation: false,
    grid: {
      borderColor: '#003399',
      borderWidth: 0
    },
    textStyle: {
      fontFamily: 'Arial, sans-serif'
    }
  };

  // Global click handler for timestamp recording
  window.addEventListener('click', function(event) {
    // Check if click is on a chart
    var chartElement = event.target.closest('[_echarts_instance_]');
    if (chartElement) {
      var chart = echarts.getInstanceByDom(chartElement);
      if (chart) {
        var rect = chartElement.getBoundingClientRect();
        var x = event.clientX - rect.left;
        var y = event.clientY - rect.top;
        var point = chart.convertFromPixel('grid', [x, y]);
        
        if (point && point[0]) {
          var timestamp = new Date(point[0]).toISOString().replace('.000Z', 'Z');
          record_timestamp(timestamp);
        }
      }
    }
  });
}

// Add synchronized vertical line at mouse position
function syncronizeCrossHairs(chart) {
  // This function is now handled by setupCrosshairs function above
  // Keep for backwards compatibility but implementation moved
}

function zoom_in_selection(event) {
  // This function will be replaced by the brush event handler in setupChartEvents
  // Keep for backwards compatibility but implementation moved to setupChartEvents
}


/* EXPORTING FUNCTIONALITY */
/* Echarts export functionality to replace Highcharts export */

/**
 * Create a global getSVG method that takes an array of charts as an argument.
 * The SVG is returned.
 */
window.getSVG = async function (charts, options) {
  const svgPromises = charts.map(async (chart, index) => {
    if (chart && chart.renderToSVGString) {
      try {
        return await chart.renderToSVGString({
          renderer: 'svg'
        });
      } catch (error) {
        console.log('Failed to get SVG for chart', index, error);
        return null;
      }
    }
    return null;
  });

  const svgResults = await Promise.all(svgPromises);
  const validSvgs = svgResults.filter(svg => svg !== null);
  
  if (validSvgs.length === 0) {
    return null;
  }

  // Combine SVGs vertically
  let combinedHeight = 0;
  let maxWidth = 0;
  const svgElements = validSvgs.map(svgString => {
    const parser = new DOMParser();
    const svgDoc = parser.parseFromString(svgString, 'image/svg+xml');
    const svgElement = svgDoc.documentElement;
    const width = parseInt(svgElement.getAttribute('width')) || 800;
    const height = parseInt(svgElement.getAttribute('height')) || 400;
    
    combinedHeight += height;
    maxWidth = Math.max(maxWidth, width);
    
    return {
      element: svgElement,
      width: width,
      height: height
    };
  });

  // Create combined SVG
  let combinedSvg = `<svg width="${maxWidth}" height="${combinedHeight}" xmlns="http://www.w3.org/2000/svg">`;
  let currentY = 0;
  
  svgElements.forEach(({element, width, height}) => {
    const innerContent = element.innerHTML;
    combinedSvg += `<g transform="translate(0,${currentY})">${innerContent}</g>`;
    currentY += height;
  });
  
  combinedSvg += '</svg>';
  return combinedSvg;
};

/**
 * Create a global exportCharts method that takes an array of charts as an
 * argument, and exporting options as the second argument
 */
window.exportCharts = async function (charts, options) {
  options = options || {};
  const format = options.type || 'image/png';
  
  try {
    if (format === 'image/svg+xml') {
      const svg = await window.getSVG(charts, options);
      if (svg) {
        downloadSVG(svg, options);
      }
    } else {
      // For other formats, we'll need to convert charts to canvas
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      
      let totalHeight = 0;
      let maxWidth = 0;
      
      // Calculate dimensions
      charts.forEach(chart => {
        if (chart && chart.getDom) {
          const dom = chart.getDom();
          maxWidth = Math.max(maxWidth, dom.offsetWidth);
          totalHeight += dom.offsetHeight;
        }
      });
      
      canvas.width = maxWidth;
      canvas.height = totalHeight;
      
      // Draw each chart to canvas
      let currentY = 0;
      for (const chart of charts) {
        if (chart && chart.getDataURL) {
          try {
            const dataUrl = chart.getDataURL({
              type: format,
              pixelRatio: 1,
              backgroundColor: 'white'
            });
            
            const img = new Image();
            img.onload = function() {
              ctx.drawImage(img, 0, currentY);
              currentY += chart.getDom().offsetHeight;
            };
            img.src = dataUrl;
          } catch (error) {
            console.log('Failed to export chart', error);
          }
        }
      }
      
      // Download the combined canvas
      setTimeout(() => {
        const link = document.createElement('a');
        link.download = options.filename || 'cluster-plots.' + (format.includes('png') ? 'png' : 'jpg');
        link.href = canvas.toDataURL(format);
        link.click();
      }, 1000);
    }
  } catch (error) {
    console.log('Failed to export charts', error);
  }
};

function downloadSVG(svg, options) {
  const blob = new Blob([svg], { type: 'image/svg+xml' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.download = options.filename || 'cluster-plots.svg';
  link.href = url;
  link.click();
  URL.revokeObjectURL(url);
}

/**
 * Create Echarts chart to plot spacecraft information
 */
window.plot_spacecraft_info = function(json_data, spacecraft_id, mission_id, info_list, min_x_value, max_x_value) {
  var data = [];
  var spacecraft_label = [];

  var available_info_list = ['X','Y','Z','r','il','mlt','l','sc_min','sc_max'];
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
  var title_info = spacecraft_name + '\n';

  for (var i = 0; i < json_data.sc_info[0].data.length; i++) {
    data.push([Date.parse(json_data.sc_info[0].data[i]), null]);
    var lab_info = [];
    for (var s = 0; s < json_data.sc_info.length-1; s++) {
      lab_info.push((json_data.sc_info[s + 1].data[i] === null ? '-' : Number(json_data.sc_info[s+1].data[i]).toFixed(1)).toString());
    }
    spacecraft_label.push([Date.parse(json_data.sc_info[0].data[i]), lab_info.join('\n')]);
  }

  for (var s = 0; s < json_data.sc_info.length-1; s++) {
    title_info += json_data.sc_info[s + 1].name + '\n';
  }

  // Add hidden info for consistent spacing
  for (var s = 0; s < available_info_list.length-1; s++) {
    if (info_list.indexOf(available_info_list[s]) === -1) {
      title_info += available_info_list[s] + '\n';
    }
  }

  var option = {
    animation: false,
    title: {
      text: title_info,
      left: 'left',
      top: 'top',
      textStyle: {
        fontSize: 11,
        color: spacecraft_color,
        fontWeight: 'bold',
        lineHeight: 20
      }
    },
    grid: {
      left: 120,
      right: 120,
      top: 10,
      bottom: 435,
      containLabel: false
    },
    xAxis: {
      type: 'time',
      min: min_x_value,
      max: max_x_value,
      boundaryGap: false,
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
        }
      },
      splitLine: {
        show: false
      },
      axisLabel: {
        show: true,
        fontSize: 11,
        margin: 25,
        align: 'right',
        formatter: function(value, index) {
          // Find corresponding label
          for (var idx = 0; idx < spacecraft_label.length; idx++) {
            if (Math.abs(spacecraft_label[idx][0] - value) < 1000) { // 1 second tolerance
              return spacecraft_label[idx][1];
            }
          }
          return '';
        }
      }
    },
    yAxis: {
      show: false
    },
    series: [{
      type: 'line',
      data: data,
      itemStyle: {
        color: spacecraft_color
      },
      lineStyle: {
        color: spacecraft_color,
        width: 1
      },
      showSymbol: false,
      silent: true
    }]
  };

  var spacecraft_info_chart = echarts.init(document.getElementById('spacecraft-info'));
  spacecraft_info_chart.setOption(option);
  spacecraft_info_chart.resize({height: 200});

  window.all_charts["spacecraft"] = spacecraft_info_chart;

  return spacecraft_info_chart;
}