// Show or hide plot borders
function manageBorder(action="show") {
  const borderable_charts = window.all_charts["plot_charts"] || [];
  const border_width = action === "show" ? 1 : 0;
  for (var i = 0; i < borderable_charts.length; i++) {
    borderable_charts[i].update({chart: { borderWidth: border_width }});
  }
}
window.manageBorder = manageBorder;


// Set the current zoom value
function set_current_zoom(current_time_inteval){
  document.getElementById("current_zoom").value = current_time_inteval;
  if(document.getElementById("previous_zoom_chain").value !== "" ){
    document.getElementById("zoom_out").classList.remove('hidden');
  }
}
window.set_current_zoom = set_current_zoom;

// Set the CEF files list
function set_cef_files_list(files_list) {
  var cef_files = files_list.split(",").map(x => x.split("/").pop()).filter(entry => entry.trim() != '');
  document.getElementById("download_cefs").dataset.cefs = cef_files.join(",");
}
window.set_cef_files_list = set_cef_files_list;
