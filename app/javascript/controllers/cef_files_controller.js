import { Controller } from "@hotwired/stimulus"

export default class extends Controller {
  zip() {
    var download_zip_button = document.getElementById("download_cefs");

    if (!download_zip_button.dataset.cefs || download_zip_button.dataset.cefs.strip === "") {
      alert("No CEF files available, please try regenerating the plots");
      return;
    }

    download_zip_button.disabled = true;

    const params = new URLSearchParams();
    params.append("cefs", download_zip_button.dataset.cefs);
    params.append("times", download_zip_button.dataset.times);
    location.assign("/plots/cef_files?" + params.toString());

    download_zip_button.disabled = false;
  }
}
