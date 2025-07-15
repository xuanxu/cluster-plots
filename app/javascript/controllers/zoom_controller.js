import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  zoomIn() {
    document.getElementById("plot_time_interval").value = document.getElementById("zoom_to").value;
    document.getElementById("submit_plots_info").click();
  }
}
