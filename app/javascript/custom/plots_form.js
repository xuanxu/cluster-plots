// Show/hide list of panels checkboxes
var toggle_panels = function() {
  var panels_listings = document.getElementById("panels");
  var panels_heading = document.getElementById("panels_heading");
  if (panels_listings.style.display === "none") {
    panels_listings.style.display = "block";
    panels_heading.innerHTML = "Panel selection <i class='fa fa-caret-down'></i>"
  } else {
    panels_listings.style.display = "none";
    panels_heading.innerHTML = "Show panel selection <i class='fa fa-caret-right'></i>"
  }
}

document.getElementById("panels_heading").addEventListener('click', toggle_panels);
