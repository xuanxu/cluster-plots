import { Controller } from "@hotwired/stimulus"
import { post } from '@rails/request.js'

// Helper function to format date (replaces Highcharts.dateFormat)
function formatDate(format, timestamp) {
  const date = new Date(timestamp);
  const pad = (n) => n < 10 ? '0' + n : n;
  
  return format
    .replace('%Y', date.getUTCFullYear())
    .replace('%m', pad(date.getUTCMonth() + 1))
    .replace('%d', pad(date.getUTCDate()))
    .replace('%H', pad(date.getUTCHours()))
    .replace('%M', pad(date.getUTCMinutes()))
    .replace('%S', pad(date.getUTCSeconds()));
}

export default class extends Controller {
  async update({ params: { nplot }}) {
    var min_level = Number(document.getElementById("min_extra_filter_" + nplot).value);
    var max_level = Number(document.getElementById("max_extra_filter_" + nplot).value);
    var loading_image = document.getElementById("loading_extra_filter_" + nplot);

    if (isNaN(min_level) || isNaN(max_level)) {
      alert("Please enter valid numeric values for the energy filter.");
      return;
    }

    if (min_level >= max_level) {
      alert("Invalid energy range: minimum value must be less than maximum value.");
      return;
    }

    loading_image.classList.add("inline");
    loading_image.classList.remove("hidden");

    var paramid = document.getElementById("extra_filter_" + nplot).dataset.paramid;
    var unit = document.getElementById("extra_filter_" + nplot).dataset.unit;
    var panel_name = document.getElementById("controls_plot_" + nplot).dataset.panelname;
    var zeroes = document.getElementById("plot_zeroes").value
    var min_x_value = window.all_charts["axis"].xAxis[0].min;
    var max_x_value = window.all_charts["axis"].xAxis[0].max;
    var datetime_start = formatDate("%Y-%m-%dT%H:%M:%SZ", min_x_value);
    var datetime_stop = formatDate("%Y-%m-%dT%H:%M:%SZ", max_x_value);

    var query_data = {
      start_at: datetime_start,
      end_at: datetime_stop,
      panel: panel_name,
      zeroes: zeroes,
      param_id: paramid,
      min_value: min_level,
      max_value: max_level
    }

    const response = await post('/plots/regenerate_panel', { body: { plot: query_data, contentType: "application/json" } })
    try {
      if (response.ok) {
        var json_response = await response.json;
        if (json_response["status"] === "OK") {
          var previous_panel = window.all_charts["plot_charts"][nplot];
          var parsed_response = JSON.parse(json_response["info"]);

          previous_panel.destroy();
          window.all_charts["plot_charts"][nplot] = plot_heatmap(parsed_response.panels_arr[0], nplot);
          previous_panel = undefined;

          var current_y_title = window.all_charts["plot_charts"][nplot].yAxis[1].axisTitle.textStr;
          var new_y_title = current_y_title.split("<br/>")[0] + "<br>" + min_level + " - " + max_level + " " + unit;
          document.getElementById("new_y_title_" + nplot).value = new_y_title;
          document.getElementById("update_y_title_" + nplot).click();
        } else if (json_response["status"] === "Error") {
          alert(json_response["info"])
        } else {
          alert("Unknown response from server");
        }
      } else {
        alert("Error getting requested data range")
      }
    } catch (e) {
      alert("There was an error getting the requested data");
    }

    loading_image.classList.remove("inline");
    loading_image.classList.add("hidden");

  }
}
