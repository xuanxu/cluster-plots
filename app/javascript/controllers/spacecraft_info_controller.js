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

}
