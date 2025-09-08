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
    borderable_charts[i].update({chart: { borderWidth: border_width }});
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
    controls = ["y_title", "y_range","z_range"];
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
    border: "0"
  };

  plot_options["grid"] = document.getElementById("grid_options").value;
  plot_options["line_thickness"] = document.getElementById("line_thickness").value;
  plot_options["font_size"] = document.getElementById("font_size").value;
  plot_options["crossline"] = String(window.visibility_crossline);
  if (window.all_charts["plot_charts"][0] != undefined){
    plot_options["border"] = String(window.all_charts["plot_charts"][0].options.chart.borderWidth) || "0";
  }

  var blob = new Blob([JSON.stringify(plot_options)], {type: "text/plain;charset=utf-8"});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "caa-plot_options-" + get_timestamp() +".json";
  a.click();
}
