import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  show_crossline() {
    var show_crossline_button = document.getElementById("show_crossline");
    show_crossline_button.style.display = "none";
    var hide_crossline_button = document.getElementById("hide_crossline");
    hide_crossline_button.style.display = "inline";
    window.visibility_crossline = 1;
  }

  hide_crossline() {
    var hide_crossline_button = document.getElementById("hide_crossline");
    hide_crossline_button.style.display = "none";
    var show_crossline_button = document.getElementById("show_crossline");
    show_crossline_button.style.display = "inline";
    window.visibility_crossline = 0;
  }

  display_border() {
    var display_border_button = document.getElementById("display_border");
    display_border_button.style.display = "none";
    var hide_border_button = document.getElementById("hide_border");
    hide_border_button.style.display = "inline";
    manageBorder("show");
  }

  hide_border() {
    var hide_border_button = document.getElementById("hide_border");
    hide_border_button.style.display = "none";
    var display_border_button = document.getElementById("display_border");
    display_border_button.style.display = "inline";
    manageBorder("hide");
  }

  show_adjusts_panel() {
    document.getElementById("show_adjusts").classList.remove("lg:inline");
    document.getElementById("show_adjusts").classList.add("lg:hidden");
    document.getElementById("hide_adjusts").classList.remove("lg:hidden");
    document.getElementById("hide_adjusts").classList.add("lg:inline");

    document.getElementById("main_plots_panel").classList.remove("col-span-10");
    document.getElementById("main_plots_panel").classList.add("col-span-8");
    document.getElementById("adjusts_panel").classList.remove("hidden");
    document.getElementById("adjusts_panel").classList.remove("col-span-0");
    document.getElementById("adjusts_panel").classList.add("col-span-2");
  }

  hide_adjusts_panel() {
    document.getElementById("hide_adjusts").classList.remove("lg:inline");
    document.getElementById("hide_adjusts").classList.add("lg:hidden");
    document.getElementById("show_adjusts").classList.remove("lg:hidden");
    document.getElementById("show_adjusts").classList.add("lg:inline");

    document.getElementById("adjusts_panel").classList.add("hidden");
    document.getElementById("adjusts_panel").classList.remove("col-span-2");
    document.getElementById("adjusts_panel").classList.add("col-span-0");
    document.getElementById("main_plots_panel").classList.remove("col-span-8");
    document.getElementById("main_plots_panel").classList.add("col-span-10");
  }

  toggle_change_title_panel() {
    const change_title_panel = document.getElementById("change_title_mini_panel");
    if (change_title_panel.classList.contains("hidden")) {
      document.getElementById("record_timestamps_mini_panel").classList.add("hidden");
      document.getElementById("record_timestamps_action").classList.remove("active");
      document.getElementById("new_plot_title").value = window.all_charts["title"].options.title.text;
      change_title_panel.classList.remove("hidden");
      change_title_panel.classList.add("block");
      document.getElementById("change_title_action").classList.add("active");
    } else {
      change_title_panel.classList.remove("block");
      change_title_panel.classList.add("hidden");
      document.getElementById("change_title_action").classList.remove("active");
    }
  }

  toggle_record_timestamps_panel() {
    const record_timestamps_panel = document.getElementById("record_timestamps_mini_panel");
    if (record_timestamps_panel.classList.contains("hidden")) {
      document.getElementById("change_title_mini_panel").classList.add("hidden");
      document.getElementById("change_title_action").classList.remove("active");
      record_timestamps_panel.classList.remove("hidden");
      record_timestamps_panel.classList.add("block");
      document.getElementById("record_timestamps_action").classList.add("active");
    } else {
      record_timestamps_panel.classList.remove("block");
      record_timestamps_panel.classList.add("hidden");
      document.getElementById("record_timestamps_action").classList.remove("active");
    }
  }

  update_plots_title() {
    window.all_charts["title"].setTitle({text: document.getElementById("new_plot_title").value});
  }

  remove_timestamp() {
    var options = document.getElementById("recorded_timestamps").options;
    var timestamp_list = document.getElementById("recorded_timestamps");
    for (var i = options.length - 1; i >= 0; i--) {
      if (options[i].selected == true) {
        timestamp_list.remove(i);
      }
    }
  }

  clear_timestamps_list() {
    var options = document.getElementById("recorded_timestamps").options.length = 0;
  }

  save_timestamps_file() {
    var timestamps_file_content = [];

    var timestamps = document.getElementById("recorded_timestamps").options;
    for (var i = 0; i < timestamps.length; i++) {
      timestamps_file_content.push(timestamps[i].value);
    }

    var blob = new Blob([timestamps_file_content.join("\n")], {type: "text/plain;charset=utf-8"});
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url;
    a.download = "CSA_timestamps_" + get_timestamp() +".txt";
    a.click();
  }

  show_y_zero_line() {
    var nplot = Number(this.element.dataset.nplot);
    window.all_charts["plot_charts"][nplot].yAxis[0].addPlotLine({
      color: '#A9A9A9',
      width: 2,
      value: 0,
      dashStyle: 'ShortDash',
			zIndex: 2,
			id: "y_zero_" + nplot
		});

    document.getElementById("y_zero_" + nplot + "_on").classList.add("hidden");
    document.getElementById("y_zero_" + nplot + "_off").classList.remove("hidden");
  }

  hide_y_zero_line() {
    var nplot = Number(this.element.dataset.nplot);
    window.all_charts["plot_charts"][nplot].yAxis[0].removePlotLine("y_zero_" + nplot);

    document.getElementById("y_zero_" + nplot + "_off").classList.add("hidden");
    document.getElementById("y_zero_" + nplot + "_on").classList.remove("hidden");
  }

  toggle_edit_plot_control({ params: { control }}){
    var nplot = Number(this.element.dataset.nplot);
    var plot_control = document.getElementById(control + "_" + nplot);
    var icon = document.getElementById(control + "_" + nplot + "_icon");
    var edit_plot_control = document.getElementById("edit_" + control + "_" + nplot);

    if (edit_plot_control.classList.contains("hidden")) {
      collapse_plot_controls(nplot, this.element.dataset.plottype);
      edit_plot_control.classList.remove("hidden");
      plot_control.classList.add("active");
      icon.classList.remove("fa-caret-down");
      icon.classList.add("fa-caret-up");
    } else {
      edit_plot_control.classList.add("hidden");
      plot_control.classList.remove("active");
      icon.classList.remove("fa-caret-up");
      icon.classList.add("fa-caret-down");
    }
  }

  update_y_title() {
    var nplot = Number(this.element.dataset.nplot);
    var plot_type = String(this.element.dataset.plottype);
    var new_y_title = document.getElementById("new_y_title_" + nplot).value;
    var axis_with_title = plot_type === "line" ? 0 : 1;
    window.all_charts["plot_charts"][nplot].yAxis[axis_with_title].setTitle({text: new_y_title});
  }

  update_y_axis_type({ params: { axis }}) {
    if (axis === "linear" || axis === "logarithmic"){
      var nplot = Number(this.element.dataset.nplot);
      var plot_type = String(this.element.dataset.plottype);
      var plot = window.all_charts["plot_charts"][nplot];
      var linear_option = document.getElementById("new_y_axis_type_" + nplot + "_linear");

      if (axis === "logarithmic" && (plot.yAxis[0].getExtremes().min <= 0 || plot.yAxis[0].getExtremes().max <= 0)) {
        alert('Can not switch to logarithmic scale: Y axis range must be positive');
        linear_option.checked = true;
      } else {
        plot.yAxis[0].update({ type: axis}, false);
        plot.yAxis[1].update({ type: axis}, true);
      }
      linear_option.focus();
      linear_option.blur();
    }
  }

  update_line_y_range({ params: { yrange }}) {
    var nplot = Number(this.element.dataset.nplot);
    var plot = window.all_charts["plot_charts"][nplot];
    var min_field = document.getElementById("min_y_range_" + nplot);
    var max_field = document.getElementById("max_y_range_" + nplot);

    if (yrange === "default"){
      min_field.value = Number(min_field.dataset.default).toFixed(3);
      max_field.value = Number(max_field.dataset.default).toFixed(3);
    } else if (yrange === "auto") {
      min_field.value = Number(min_field.dataset.auto).toFixed(3);
      max_field.value = Number(max_field.dataset.auto).toFixed(3);
    } else if (yrange === "custom") {
      min_field.value = Number(min_field.value);
      max_field.value = Number(max_field.value);
      document.getElementById("new_y_range_" + nplot + "_default").checked = false;
      if (document.getElementById("new_y_range_" + nplot + "_auto")){
        document.getElementById("new_y_range_" + nplot + "_auto").checked = false;
      }
    }

    if (document.getElementById("new_y_axis_type_" + nplot + "_logarithmic").checked) {
      if (min_field.value <= 0) {
        alert("Can not set Y range with negative or zero values in logarithmic scale: Adjusting range to minimum positive value");
        min_field.value = 0.000001.toExponential(2);
      }
      if (max_field.value <= 0) {
        max_field.value = 0.00001.toExponential(2);
      }
    }

    var min_value = Number(min_field.value);
    var max_value = Number(max_field.value);
    if (isNaN(min_value) || isNaN(max_value) || min_value >= max_value) {
      alert("Invalid Y range values. Please enter valid numbers.");
      return;
    } else {
      plot.yAxis[0].setExtremes(min_value, max_value, false);
      plot.yAxis[1].setExtremes(min_value, max_value);
      max_field.focus();
      max_field.blur();
    }
  }

  update_spectogram_y_range({ params: { yrange }}) {
    var nplot = Number(this.element.dataset.nplot);
    var plot = window.all_charts["plot_charts"][nplot];
    var min_field = document.getElementById("min_y_range_" + nplot);
    var max_field = document.getElementById("max_y_range_" + nplot);
    var min_default = Number(min_field.dataset.default);
    var max_default = Number(max_field.dataset.default);
    var y_type = min_field.dataset.ytype;

    if (yrange === "default"){
      min_field.value = min_default.toFixed(1);
      max_field.value = max_default.toFixed(1);
    } else if (yrange === "custom") {
      min_field.value = Number(min_field.value);
      max_field.value = Number(max_field.value);
      document.getElementById("new_y_range_" + nplot + "_default").checked = false;
    }

    var min_value = Number(min_field.value);
    var max_value = Number(max_field.value);
    if (isNaN(min_value) || isNaN(max_value) || min_value >= max_value) {
      alert("Invalid Y range values. Please enter valid numbers.");
      return;
    } else if ((min_value < min_default) || (max_value > max_default)) {
      alert("The selected range can't exceed the original one : [" + min_default + ', ' + max_default + "]" );
      return;
    } else {
      var min_value_data = min_value;
      var max_value_data = max_value;

      if (y_type != "linear") {
        min_value_data = Math.log10(min_value);
        max_value_data = Math.log10(max_value);
      }

      plot.yAxis[0].setExtremes(min_value_data, max_value_data, false);
      plot.yAxis[1].setExtremes(min_value, max_value);
      max_field.focus();
      max_field.blur();
    }
  }

  update_z_range({ params: { zrange }}) {
    var nplot = Number(this.element.dataset.nplot);
    var plot = window.all_charts["plot_charts"][nplot];
    var min_field = document.getElementById("min_z_range_" + nplot);
    var max_field = document.getElementById("max_z_range_" + nplot);
    var min_value = Number(min_field.dataset.default);
    var max_value = Number(max_field.dataset.default);

    if (zrange === "custom") {
      min_value = Number(min_field.value);
      max_value = Number(max_field.value);
      document.getElementById("new_z_range_" + nplot + "_default").checked = false;
    }

    if (isNaN(min_value) || isNaN(max_value) || min_value >= max_value) {
      alert("Invalid Z range values. Please enter valid numbers.");
      return;
    } else {
      min_field.value = min_value.toExponential(2);
      max_field.value = max_value.toExponential(2);
      plot.colorAxis[0].update({min: min_value, max: max_value });
      max_field.focus();
      max_field.blur();
    }
  }

  export_plot() {
    var download_type = document.getElementById("save_plot").value;
    var charts_to_plot = []
    var filename_dates = "";
    if (typeof(chart_start_datetime) !== "undefined" && typeof(chart_stop_datetime) !== "undefined"){
      filename_dates = "_" + chart_start_datetime + "_" + chart_stop_datetime;
      filename_dates = filename_dates.replace(/[TZ:-]/g, "");
    }
    if (download_type != "") {
      charts_to_plot = [window.all_charts["title"], ...window.all_charts["plot_charts"], window.all_charts["axis"]]
      if (window.all_charts["spacecraft"] != undefined) {
        charts_to_plot.push(window.all_charts["spacecraft"]);
      }
      Highcharts.exportCharts(charts_to_plot, {type: download_type, filename: "Cluster_Plot" + filename_dates});
      document.getElementById("save_plot").value = "";
    }
  }

  grid_display(){
    var grid_option = document.getElementById("grid_options").value;
    var major_grid = 1;
    var minor_grid = 1;

    if(grid_option === 'major'){
      minor_grid = 0;
    } else if (grid_option === 'off'){
      major_grid = 0;
      minor_grid = 0;
    } else {
      document.getElementById("grid_options").value = "";
    }

    window.all_charts["plot_charts"].forEach(plot_chart => {
      plot_chart.yAxis.forEach(y_axis => {
        y_axis.update({ gridLineWidth: major_grid, minorGridLineWidth: minor_grid });
      });
      plot_chart.xAxis[0].update({ gridLineWidth: major_grid, minorGridLineWidth: minor_grid });
    });
  }

  line_thickness(){
    var line_thickness_option = document.getElementById("line_thickness").value;
    if (Number(line_thickness_option) < 1 || Number(line_thickness_option) > 4) {
      line_thickness_option = 2;
      document.getElementById("line_thickness").value = "";
    }
    if (line_thickness_option === "") { line_thickness_option = 2 }

    window.all_charts["plot_charts"].forEach(plot_chart => {
      plot_chart.series.forEach(plot_serie => {
        if(plot_serie.type === "line") { plot_serie.update({ lineWidth: line_thickness_option }) }
      });
    });
  }

  font_size(){
    var font_size_option = document.getElementById("font_size").value;
    if (Number(font_size_option) < 9 || Number(font_size_option) > 16) {
      font_size_option = 11;
      document.getElementById("font_size").value = "";
    }
    if (font_size_option === "") { font_size_option = 11}

    window.all_charts["plot_charts"].forEach(plot_chart => {
      plot_chart.yAxis[0].update({ labels: { style: { fontSize: font_size_option } }, title: { style: { fontSize: font_size_option } }});
      
      if (plot_chart.series[0].type === "heatmap") {
        plot_chart.yAxis[1].update({ labels: { style: { fontSize: font_size_option } }, title: { style: { fontSize: font_size_option } }});
        plot_chart.colorAxis[0].update({ labels: { style :{ fontSize: font_size_option } }});
      }
    });

    window.all_charts["axis"].xAxis[0].update({ labels: { style :{ fontSize: font_size_option } }});

    if (window.all_charts["spacecraft"] != undefined) {
      const font_for_spacecraft_plot = Math.min(font_size_option, 11);
      window.all_charts["spacecraft"].xAxis[0].update({ labels: { style :{ fontSize: font_for_spacecraft_plot } }});
      window.all_charts["spacecraft"].yAxis[0].update({ title: { style :{ fontSize: font_for_spacecraft_plot } }});
    }
  }

  import_export_options(){
    var import_export_selector = document.getElementById("save_or_export_options");
    var action_to_perform = import_export_selector.value;

    if (action_to_perform === "save") {
      save_plot_options();
    } else if (action_to_perform === "import") {
      document.getElementById("import_plot_options_file").click();
    }

    import_export_selector.value = "";
  }

  load_plot_options(){
    var options_file = document.getElementById('import_plot_options_file').files[0];
    var reader = new FileReader();

    var loading_image = document.getElementById("loading_plot_options");
    loading_image.classList.add("inline");
    loading_image.classList.remove("hidden");

    reader.onload = function(event){
      try {
        var plot_options = JSON.parse(event.target.result);
        if ("grid" in plot_options){
          document.getElementById("grid_options").value = plot_options.grid;
          document.getElementById("grid_options").dispatchEvent(new Event('change'))
        }
        if ("line_thickness" in plot_options){
          document.getElementById("line_thickness").value = plot_options.line_thickness;
          document.getElementById("line_thickness").dispatchEvent(new Event('change'))
        }
        if ("font_size" in plot_options){
          document.getElementById("font_size").value = plot_options.font_size;
          document.getElementById("font_size").dispatchEvent(new Event('change'))
        }
        if ("crossline" in plot_options){
          if ((Number(plot_options.crossline) === 1) && (window.visibility_crossline === 0)){
            document.getElementById("show_crossline").click();
          } else if ((Number(plot_options.crossline) === 0) && (window.visibility_crossline === 1)){
            document.getElementById("hide_crossline").click();
          }
        }
        if ("border" in plot_options){
          if (Number(plot_options.border) === 1) {
            document.getElementById("display_border").click();
          } else if (Number(plot_options.border) === 0){
            document.getElementById("hide_border").click();
          }
        }
        alert("Plot options applied!");
      } catch (e) {
        alert("There was an error reading the file, make sure the content is valid JSON.");
      } finally {
        loading_image.classList.add("hidden");
        loading_image.classList.remove("inline");
      }
    }
    if(options_file){
      reader.readAsText(options_file);
    }
  }

}
