import { Controller } from "@hotwired/stimulus"
import { post } from '@rails/request.js'

export default class extends Controller {

  toggle_controls() {
    var heading = document.getElementById("spacecraft_info_heading");
    var controls_container = document.getElementById("spacecraft_info_controls");

    if (controls_container.classList.contains("hidden")) {
      controls_container.classList.add("block");
      controls_container.classList.remove("hidden");
      heading.innerHTML = "Spacecraft info <i class='fa fa-caret-down'></i>"
    } else {
      controls_container.classList.add("hidden");
      controls_container.classList.remove("block");
      heading.innerHTML = "Add spacecraft info <i class='fa fa-caret-right'></i>"
    }
  }

  show_options({ params: { mission } }){
    var cluster_options = document.getElementById("cluster_spacecraft_options");
    var double_star_options = document.getElementById("double_star_spacecraft_options");

    var cluster_link = document.getElementById("spacecraft_info_cluster");
    var double_star_link = document.getElementById("spacecraft_info_double_star");

    if (mission === "cluster") {
      cluster_options.classList.remove("hidden");
      double_star_options.classList.add("hidden");
      cluster_link.classList.add("spacecraft_mission_selected");
      double_star_link.classList.remove("spacecraft_mission_selected");
    } else if (mission === "double_star") {
      double_star_options.classList.remove("hidden");
      cluster_options.classList.add("hidden");
      double_star_link.classList.add("spacecraft_mission_selected");
      cluster_link.classList.remove("spacecraft_mission_selected");
    }
  }

  action_on_all({ params: { mission, action } }){
    if (mission === "cluster") {
      var options = document.getElementById("cluster_spacecraft_list").querySelectorAll("input[type='checkbox']");
    } else if (mission === "double_star") {
      var options = document.getElementById("double_star_spacecraft_list").querySelectorAll("input[type='checkbox']");
    }

    for (var i = 0; i < options.length; i++) {
      options[i].checked = (action === "select");
    }
  }

  async add_spacecraft_info({ params: { mission } }){
    var spacecraft_code = 0;
    var mission_code = 0;
    var options = null;
    var info_list = [];
    var ticks_iso = [];
    var loading_image = null;

    if (mission === "cluster") {
      if (document.getElementById('C1').checked == true) {
          spacecraft_code = 1;
      } else if (document.getElementById('C2').checked == true) {
          spacecraft_code = 2;
      } else if (document.getElementById('C3').checked == true) {
          spacecraft_code = 3;
      } else if (document.getElementById('C4').checked == true) {
          spacecraft_code = 4;
      } else {
          alert('Please select a spacecraft');
          return;
      }
      mission_code = 1;
      options = document.getElementById("cluster_spacecraft_list").querySelectorAll("input[type='checkbox']");
      loading_image = document.getElementById("loading_cluster");
    } else if (mission === "double_star"){
      if (document.getElementById('D1').checked == true) {
          spacecraft_code = 1;
      } else if (document.getElementById('D2').checked == true) {
          spacecraft_code = 2;
      } else {
          alert('Please select a spacecraft');
          return;
      }
      mission_code = 2;
      options = document.getElementById("double_star_spacecraft_list").querySelectorAll("input[type='checkbox']");
      loading_image = document.getElementById("loading_double_star");
    } else {
      alert('Invalid mission');
      return;
    }

    for (var i = 0; i < options.length; i++) {
      if (options[i].checked) {
        info_list.push(options[i].value);
      }
    }
    if (info_list.length === 0) {
      alert('You have not selected any parameter');
      return;
    }

    var ticks = window.all_charts["plot_charts"][0].xAxis[0].tickPositions;
    for (var t = 0; t < ticks.length; t++) {
      ticks_iso.push(Highcharts.dateFormat( "%Y-%m-%dT%H:%M:%SZ", ticks[t]));
    }

    var min_x_value = window.all_charts["axis"].xAxis[0].min;
    var max_x_value = window.all_charts["axis"].xAxis[0].max;
    var datetime_start = Highcharts.dateFormat("%Y-%m-%dT%H:%M:%SZ", min_x_value);
    var datetime_stop = Highcharts.dateFormat("%Y-%m-%dT%H:%M:%SZ", max_x_value);

    var query_data = {
      start_at: datetime_start,
      end_at: datetime_stop,
      time_ticks: ticks_iso,
      mission: mission_code,
      spacecraft: spacecraft_code,
      info_list: info_list
    }

    loading_image.classList.add("inline");
    loading_image.classList.remove("hidden");

    var remove_cluster_link = document.getElementById("remove_cluster");
    var remove_double_star_link = document.getElementById("remove_double_star");

    var request_path = url_prefix() + "/plots/spacecraft_info";
    const response = await post(request_path, { body: { spacecraft_info: query_data, contentType: "application/json" } })
    if (response.ok) {
      var json_response = await response.json;
      if (json_response["status"] === "OK") {
        const info = JSON.parse(json_response["info"]);
        plot_spacecraft_info(info, spacecraft_code, mission_code, info_list, min_x_value, max_x_value);

        remove_cluster_link.classList.remove("spacecraft_action_disabled");
        remove_cluster_link.classList.add("spacecraft_action");
        remove_double_star_link.classList.remove("spacecraft_action_disabled");
        remove_double_star_link.classList.add("spacecraft_action");
      } else if (json_response["status"] === "Error") {
        alert("Request failed: " + json_response["info"]);
      } else {
        alert("Unknown response from server");
      }
    } else {
      alert("Error getting spacecraft info")
    }

    loading_image.classList.add("hidden");
    loading_image.classList.remove("inline");
  }

  remove_spacecraft_info_plot() {
    if (window.all_charts["spacecraft"] != undefined) {
      window.all_charts["spacecraft"].destroy();
      window.all_charts["spacecraft"] = undefined;

      var remove_cluster_link = document.getElementById("remove_cluster");
      var remove_double_star_link = document.getElementById("remove_double_star");
      remove_cluster_link.classList.add("spacecraft_action_disabled");
      remove_cluster_link.classList.remove("spacecraft_action");
      remove_double_star_link.classList.add("spacecraft_action_disabled");
      remove_double_star_link.classList.remove("spacecraft_action");
    }
  }

}
