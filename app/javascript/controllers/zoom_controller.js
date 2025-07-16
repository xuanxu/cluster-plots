import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  zoom_in() {
    const current_time_interval = document.getElementById("current_zoom").value;
    var previous_zooms = document.getElementById("previous_zoom_chain").value.split(',').filter(entry => entry.trim() != '');
    previous_zooms.unshift(current_time_interval);

    document.getElementById("previous_zoom_chain").value = previous_zooms.join(',');
    document.getElementById("plot_time_interval").value = document.getElementById("zoom_to").value;
    document.getElementById("current_zoom").value = "";
    document.getElementById("zoom_to").value = "";
    document.getElementById("submit_plots_info").click();
  }

  zoom_back() {
    var previous_zooms = document.getElementById("previous_zoom_chain").value.split(',').filter(entry => entry.trim() != '');
    if (previous_zooms.length > 0) {
      var zomm_back_to = previous_zooms.shift();

      document.getElementById("current_zoom").value = "";
      document.getElementById("zoom_to").value = "";
      document.getElementById("previous_zoom_chain").value = previous_zooms.join(',');
      document.getElementById("plot_time_interval").value = zomm_back_to;
      document.getElementById("submit_plots_info").click();
    }
  }
}
