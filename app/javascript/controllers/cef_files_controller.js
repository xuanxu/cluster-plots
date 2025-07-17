import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  zip() {
    var download_zip_button = document.getElementById("download_cefs");
    download_zip_button.disabled = true;
    alert("Create zip file for: " + download_zip_button.dataset.cefs);
  }
}
