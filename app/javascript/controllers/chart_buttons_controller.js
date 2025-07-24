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
}
