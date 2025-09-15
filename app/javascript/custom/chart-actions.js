// Show or hide plot borders
function manageBorder(action="show") {
  var borderable_charts =  [...window.all_charts["plot_charts"]];
  if (window.all_charts["axis"] != undefined) {
    borderable_charts.push(window.all_charts["axis"]);
  }
  if (window.all_charts["spacecraft"] != undefined) {
    borderable_charts.push(window.all_charts["spacecraft"]);
  }
  const border_width = action === "show" ? 1 : 0;
  for (var i = 0; i < borderable_charts.length; i++) {
    if (borderable_charts[i] && borderable_charts[i].setOption) {
      borderable_charts[i].setOption({
        grid: { 
          borderWidth: border_width,
          borderColor: border_width > 0 ? '#000' : 'transparent'
        }
      });
    }
  }
}
window.manageBorder = manageBorder;

// Set the current zoom value
function set_current_zoom(current_time_inteval){
  document.getElementById("current_zoom").value = current_time_inteval;
  if(document.getElementById("previous_zoom_chain").value !== "" ){
    document.getElementById("zoom_out").classList.remove('hidden');
  }
}
window.set_current_zoom = set_current_zoom;

// Set the CEF files list
function set_cef_files_list(files_list) {
  var cef_files = files_list.split(",").map(x => x.split("/").pop()).filter(entry => entry.trim() != '');
  document.getElementById("download_cefs").dataset.cefs = cef_files.join(",");
  if (typeof(chart_start_datetime) !== "undefined" && typeof(chart_stop_datetime) !== "undefined") {
    document.getElementById("download_cefs").dataset.times = chart_start_datetime + "-" + chart_stop_datetime;
  }
}
window.set_cef_files_list = set_cef_files_list;

// Add entry to timepstamps list
function record_timestamp(new_timestamp) {
  var timestamp_list = document.getElementById("recorded_timestamps");
  if (typeof(new_timestamp)!== "undefined" && new_timestamp !== null) {
    var option = document.createElement("option");
    option.value = new_timestamp;
    option.text = new_timestamp;
    option.className = "animation_text_in";
    timestamp_list.prepend(option);
  }
}
window.record_timestamp = record_timestamp;

// Collapse plot controls
// nplot is the plot number, plot_type is the type of plot (line or spectrogram)
window.collapse_plot_controls = function(nplot, plot_type) {
  var controls = [];
  if (plot_type === "line") {
    controls = ["y_title", "y_range", "y_axis_type"];
  } else if (plot_type === "spectrogram") {
    controls = ["y_title", "y_range","z_range", "extra_filter"];
  }
  controls.forEach(control => {
    var control_element = document.getElementById(control + "_" + nplot);
    if (control_element && control_element.classList.contains("active")){
      control_element.classList.remove("active");
      document.getElementById("edit_" + control + "_" + nplot).classList.add("hidden");
      var icon = document.getElementById(control + "_" + nplot + "_icon");
      icon.classList.remove("fa-caret-up");
      icon.classList.add("fa-caret-down");
    }
  });
}

window.save_plot_options = function(){
  var plot_options = {
    grid: "",
    line_thickness: "",
    font_size: "",
    crossline: "0",
    border: "0",
    plots: {}
  };

  plot_options["grid"] = document.getElementById("grid_options").value;
  plot_options["line_thickness"] = document.getElementById("line_thickness").value;
  plot_options["font_size"] = document.getElementById("font_size").value;
  plot_options["crossline"] = String(window.visibility_crossline);

  var nplots = window.all_charts["plot_charts"].length;
  if (nplots > 0) {
    // For Echarts, we need to get border info differently
    var firstChart = window.all_charts["plot_charts"][0];
    if (firstChart && firstChart.getOption) {
      var option = firstChart.getOption();
      plot_options["border"] = (option.grid && option.grid[0] && option.grid[0].borderWidth) ? "1" : "0";
    }

    for (var n = 0; n < window.all_charts["plot_charts"].length; n++) {
      var chart = window.all_charts["plot_charts"][n];
      var chart_controls = document.getElementById("controls_plot_" + n);
      if (chart_controls && chart.getOption) {
        var plot_type = chart_controls.dataset.plottype;
        var option = chart.getOption();
        
        if (plot_type === "line"){
          var line_plot_options = {
            y_title: option.yAxis && option.yAxis[0] ? option.yAxis[0].name : ""
          }

          if (document.getElementById("new_y_axis_type_" + n + "_linear").checked) {
            line_plot_options["y_axis_type"] = "linear";
          } else if (document.getElementById("new_y_axis_type_" + n + "_logarithmic").checked) {
            line_plot_options["y_axis_type"] = "logarithmic";
          }

          if (document.getElementById("new_y_range_" + n + "_auto").checked) {
            line_plot_options["y_range"] = "auto";
          } else if (document.getElementById("new_y_range_" + n + "_default").checked) {
            line_plot_options["y_range"] = "default";
          } else {
            line_plot_options["y_range"] = "custom";
          }
          line_plot_options["y_range_values"] = {
            min: document.getElementById("min_y_range_" + n).value,
            max: document.getElementById("max_y_range_" + n).value
          }

          if (document.getElementById("y_zero_" + n + "_on").classList.contains("hidden")) {
            line_plot_options["y_zero_line"] = "on";
          } else {
            line_plot_options["y_zero_line"] = "off";
          }

          plot_options["plots"][chart_controls.dataset.panelname] = line_plot_options;
        } else if (plot_type === "spectrogram"){
          var spectrogram_plot_options = {
            y_title: option.yAxis && option.yAxis[0] ? option.yAxis[0].name : "",
          }

          if (document.getElementById("new_y_range_" + n + "_default").checked) {
            spectrogram_plot_options["y_range"] = "default";
          } else {
            spectrogram_plot_options["y_range"] = "custom";
          }
          spectrogram_plot_options["y_range_values"] = {
            min: document.getElementById("min_y_range_" + n).value,
            max: document.getElementById("max_y_range_" + n).value
          }

          if (document.getElementById("new_z_range_" + n + "_default").checked) {
            spectrogram_plot_options["z_range"] = "default";
          } else {
            spectrogram_plot_options["z_range"] = "custom";
          }
          spectrogram_plot_options["z_range_values"] = {
            min: document.getElementById("min_z_range_" + n).value,
            max: document.getElementById("max_z_range_" + n).value
          }

          plot_options["plots"][chart_controls.dataset.panelname] = spectrogram_plot_options;
        }
      }
    }
  }

  var blob = new Blob([JSON.stringify(plot_options, null, 2)], {type: "application/json"});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "caa-plot_options-" + get_timestamp() +".json";
  a.click();
}

// Helper function to generate timestamp
function get_timestamp() {
  var now = new Date();
  return now.getFullYear() + 
         String(now.getMonth() + 1).padStart(2, '0') + 
         String(now.getDate()).padStart(2, '0') + '_' +
         String(now.getHours()).padStart(2, '0') + 
         String(now.getMinutes()).padStart(2, '0') + 
         String(now.getSeconds()).padStart(2, '0');
}
