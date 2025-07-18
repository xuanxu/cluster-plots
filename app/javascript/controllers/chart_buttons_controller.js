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
}
