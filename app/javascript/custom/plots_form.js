// Reset panel selection
var unselect_all_panels = function(event) {
  event.preventDefault();
  event.stopPropagation();
  var panel_list = document.getElementById("panel_list");
  var selected_options = panel_list.options;
  for (var i = selected_options.length - 1; i >= 0; i--) {
    panel_list.remove(i);
  }
  var panel_checkboxes = document.getElementsByClassName("panel_checkbox");
  for (var i = 0; i < panel_checkboxes.length; i++) {
    panel_checkboxes[i].checked = false;
  }
  var zeroes_filters = document.getElementsByClassName("zero_checkbox");
  for (var i = 0; i < zeroes_filters.length; i++) {
    zeroes_filters[i].checked = false;
  }
}
document.getElementById("clear_panel_selection").addEventListener('click', function(event) { unselect_all_panels(event) });

// Set start and stop datetimes
function set_plot_times(initial_datetime, end_datetime) {
  document.getElementById("start_date").value = initial_datetime.slice(0, 10);
  document.getElementById("start_time").value = initial_datetime.slice(11, 19);

  document.getElementById("stop_date").value = end_datetime.slice(0, 10);
  document.getElementById("stop_time").value = end_datetime.slice(11, 19);

  document.getElementById("plot_times").innerHTML = initial_datetime + " " + end_datetime;
  document.getElementById("plot_time_interval").value = initial_datetime + " " + end_datetime;

  document.getElementById("stop_time").dispatchEvent(new Event('change'))
}
window.set_plot_times = set_plot_times;

// Update plot times
function update_plot_times() {
  var start_date = document.getElementById("start_date");
  var start_time = document.getElementById("start_time");
  var stop_date = document.getElementById("stop_date");
  var stop_time = document.getElementById("stop_time");

  var plot_time_interval_value = start_date.value + "T" + start_time.value + "Z " + stop_date.value + "T" + stop_time.value + "Z";
  document.getElementById("plot_times").innerHTML = plot_time_interval_value;
  document.getElementById("plot_time_interval").value = plot_time_interval_value;
}

// Show/hide list of panels checkboxes
var toggle_panels = function() {
  var panels_listings = document.getElementById("panels");
  var panels_heading = document.getElementById("panels_heading");
  var clear_panels_link = document.getElementById("clear_panel_selection");
  if (panels_listings.style.display === "none") {
    panels_listings.style.display = "block";
    panels_heading.innerHTML = "Panel selection <i class='fa fa-caret-down'></i>"
    clear_panels_link.style.display = "inline";
  } else {
    panels_listings.style.display = "none";
    panels_heading.innerHTML = "Show panel selection <i class='fa fa-caret-right'></i>"
    clear_panels_link.style.display = "none";
  }
}
document.getElementById("panels_heading").addEventListener('click', toggle_panels);

// Hide panel selection
var hide_panels = function() {
  var panels_listings = document.getElementById("panels");
  var panels_heading = document.getElementById("panels_heading");
  var clear_panels_link = document.getElementById("clear_panel_selection");
  panels_listings.style.display = "none";
  panels_heading.innerHTML = "Show panel selection <i class='fa fa-caret-right'></i>"
  clear_panels_link.style.display = "none";
}

// Show loading info
var show_loading_info = function() {
  var plots_info_container = document.getElementById("plots_container_wrapper");
  plots_info_container.style.display = "none";
  var loading_info = document.getElementById("loading_info");
  loading_info.style.display = "block";
}

// Show/hide duration fields
var show_duration = function(event) {
  event.preventDefault();
  var duration_fields = document.getElementById("duration_fields");
  var show_duration_heading = document.getElementById("show_duration_heading");
  duration_fields.style.display = "block";
  show_duration_heading.style.display = "none";
}
var hide_duration = function(event) {
  event.preventDefault();
  var duration_fields = document.getElementById("duration_fields");
  var show_duration_heading = document.getElementById("show_duration_heading");
  duration_fields.style.display = "none";
  show_duration_heading.style.display = "inline";
}
document.getElementById("show_duration_heading").addEventListener('click', function(event) { show_duration(event) });
document.getElementById("hide_duration_heading").addEventListener('click', function(event) { hide_duration(event) });

// Update duration fields when start and stop times are changed
var sync_duration = function() {
  var start_date = document.getElementById("start_date");
  var start_time = document.getElementById("start_time");
  var stop_date = document.getElementById("stop_date");
  var stop_time = document.getElementById("stop_time");
  var duration_days = document.getElementById("duration_days");
  var duration_hours = document.getElementById("duration_hours");
  var duration_minutes = document.getElementById("duration_minutes");
  var duration_seconds = document.getElementById("duration_seconds");

  var start = new Date(start_date.value + " " + start_time.value);
  var stop = new Date(stop_date.value + " " + stop_time.value);
  var diff = stop - start;

  if (diff < 0) {
    duration_days.value = 0;
    duration_hours.value = 0;
    duration_minutes.value = 0;
    duration_seconds.value = 0;
  } else {
  var hours = Math.floor(diff / 1000 / 60 / 60);
  var minutes = Math.floor(diff / 1000 / 60 % 60);
  var seconds = Math.floor(diff / 1000 % 60);
  duration_days.value = Math.floor(hours / 24);
  duration_hours.value = hours % 24;
  duration_minutes.value = minutes;
  duration_seconds.value = seconds;

  update_plot_times();
  }
}
document.getElementById("start_date").addEventListener('change', sync_duration);
document.getElementById("start_time").addEventListener('change', sync_duration);
document.getElementById("stop_date").addEventListener('change', sync_duration);
document.getElementById("stop_time").addEventListener('change', sync_duration);

// Update stop time when duration is changed
var sync_stop_time = function() {
  var start_date = document.getElementById("start_date");
  var start_time = document.getElementById("start_time");
  var stop_date = document.getElementById("stop_date");
  var stop_time = document.getElementById("stop_time");
  var duration_days = document.getElementById("duration_days");
  var duration_hours = document.getElementById("duration_hours");
  var duration_minutes = document.getElementById("duration_minutes");
  var duration_seconds = document.getElementById("duration_seconds");

  var stop = new Date(start_date.value + " " + start_time.value + "Z");
  stop.setDate(stop.getDate() + parseInt(duration_days.value || 0));
  stop.setHours(stop.getHours() + parseInt(duration_hours.value));
  stop.setMinutes(stop.getMinutes() + parseInt(duration_minutes.value));
  stop.setSeconds(stop.getSeconds() + parseInt(duration_seconds.value));

  stop_date.value = stop.toISOString().slice(0, 10);
  stop_time.value = stop.toISOString().slice(11, 19);

  update_plot_times();
}
document.getElementById("duration_days").addEventListener('change', sync_stop_time);
document.getElementById("duration_hours").addEventListener('change', sync_stop_time);
document.getElementById("duration_minutes").addEventListener('change', sync_stop_time);
document.getElementById("duration_seconds").addEventListener('change', sync_stop_time);

// Calculate times for next interval with set duration
function next_interval() {
  var start_date = document.getElementById("start_date");
  var start_time = document.getElementById("start_time");
  var stop_date = document.getElementById("stop_date");
  var stop_time = document.getElementById("stop_time");

  start_date.value = stop_date.value;
  start_time.value = stop_time.value;

  sync_stop_time();
}
document.getElementById("next_interval").addEventListener('click', next_interval);

// Calculate times for previous interval with set duration
function previous_interval() {
  var start_date = document.getElementById("start_date");
  var start_time = document.getElementById("start_time");
  var duration_days = document.getElementById("duration_days");
  var duration_hours = document.getElementById("duration_hours");
  var duration_minutes = document.getElementById("duration_minutes");
  var duration_seconds = document.getElementById("duration_seconds");

  var new_start = new Date(start_date.value + " " + start_time.value + "Z");
  new_start.setDate(new_start.getDate() - parseInt(duration_days.value));
  new_start.setHours(new_start.getHours() - parseInt(duration_hours.value));
  new_start.setMinutes(new_start.getMinutes() - parseInt(duration_minutes.value));
  new_start.setSeconds(new_start.getSeconds() - parseInt(duration_seconds.value));

  start_date.value = new_start.toISOString().slice(0, 10);
  start_time.value = new_start.toISOString().slice(11, 19);

  sync_stop_time();
}
document.getElementById("previous_interval").addEventListener('click', previous_interval);

// Select mission tabs
const mission_links = document.querySelectorAll('nav a.mission_option');
function select_mission(event){
  event.preventDefault();
  var clicked_link = event.currentTarget;
  mission_links.forEach(mission_link => {
    mission_link.classList.remove('mission_selected');
  });
  clicked_link.classList.add('mission_selected');

  const mission_panels_lists = document.querySelectorAll('div.mission_panels_list');
  mission_panels_lists.forEach(mission_panels_list => {
    mission_panels_list.style.display = "none";
  });
  const mission_panels_list = document.getElementById(clicked_link.id + "_panels");
  mission_panels_list.style.display = "block";
}
mission_links.forEach(mission_link => {
  mission_link.addEventListener('click', function(event) { select_mission(event); });
});

// Select instrument tabs
const instrument_links = document.querySelectorAll('nav a.instrument_option');
function select_instrument(event){
  event.preventDefault();
  var clicked_link = event.currentTarget;
  const mission_instrument_links = document.querySelectorAll('nav a.' + clicked_link.dataset.mission);
  mission_instrument_links.forEach(instrument_link => {
    instrument_link.classList.remove('instrument_selected');
  });
  clicked_link.classList.add('instrument_selected');

  const instrument_panels_lists = document.querySelectorAll('div.' + clicked_link.dataset.mission + '_instrument_panels_list');
  instrument_panels_lists.forEach(instrument_panels_list => {
    instrument_panels_list.style.display = "none";
  });
  const instrument_panels_list = document.getElementById(clicked_link.id + "_panels");
  instrument_panels_list.style.display = "block";
}
instrument_links.forEach(instrument_link => {
  instrument_link.addEventListener('click', function(event) { select_instrument(event); });
});

// Add/remove selected panel when checkbox is clicked
function select_panel(event) {
  var panel = event.currentTarget;
  var panel_list = document.getElementById("panel_list");

  if (panel.checked) {
    var option = document.createElement("option");
    option.value = panel.dataset.panel_code;
    option.id = "selected_panel_" + panel.id;
    option.text = panel.value;
    option.dataset.origin_checkbox_id = panel.id;
    option.className = "animation_text_in";
    panel_list.add(option);
  } else {
    var option_list = panel_list.options;
    for (var i = 0; i < option_list.length; i++) {
      if (option_list[i].id === "selected_panel_" + panel.id) {
        option_list.remove(i);
      }
    }
  }
}
const panel_checkboxes = document.querySelectorAll('input.panel_checkbox');
panel_checkboxes.forEach(panel_checkbox => {
  panel_checkbox.addEventListener('change', function(event) { select_panel(event); });
});

// Move selection up in the panel list
function move_up(event) {
  var options = document.getElementById("panel_list").options;
  for (var i = 0; i < options.length; i++) {
    if (options[i].selected == true && i > 0) {
      var selected_option = options[i];
      var previous_option = options[i - 1];
      var tmp_option_data = [selected_option.id, selected_option.value, selected_option.text, selected_option.dataset.origin_checkbox_id];
      var tmp_previous_data = [previous_option.id, previous_option.value, previous_option.text, previous_option.dataset.origin_checkbox_id];
      previous_option.id = tmp_option_data[0];
      previous_option.value = tmp_option_data[1];
      previous_option.text = tmp_option_data[2];
      previous_option.dataset.origin_checkbox_id = tmp_option_data[3];
      previous_option.selected = true;
      selected_option.id = tmp_previous_data[0];
      selected_option.value = tmp_previous_data[1];
      selected_option.text = tmp_previous_data[2];
      selected_option.dataset.origin_checkbox_id = tmp_previous_data[3];
      selected_option.selected = false;
    }
  }
}
document.getElementById("move_panel_up").addEventListener('click', move_up);

// Move selection down in the panel list
function move_down(event) {
  var options = document.getElementById("panel_list").options;
  for (var i = options.length - 1; i >= 0; i--) {
    if (options[i].selected == true && i < options.length - 1) {
      var selected_option = options[i];
      var next_option = options[i + 1];
      var tmp_option_data = [selected_option.id, selected_option.value, selected_option.text, selected_option.dataset.origin_checkbox_id];
      var tmp_next_data = [next_option.id, next_option.value, next_option.text, next_option.dataset.origin_checkbox_id];
      next_option.id = tmp_option_data[0];
      next_option.value = tmp_option_data[1];
      next_option.text = tmp_option_data[2];
      next_option.dataset.origin_checkbox_id = tmp_option_data[3];
      next_option.selected = true;
      selected_option.id = tmp_next_data[0];
      selected_option.value = tmp_next_data[1];
      selected_option.text = tmp_next_data[2];
      selected_option.dataset.origin_checkbox_id = tmp_next_data[3];
      selected_option.selected = false;
    }
  }
}
document.getElementById("move_panel_down").addEventListener('click', move_down);

// Remove selected panels from the list
function remove_panel(event) {
  var options = document.getElementById("panel_list").options;
  var panel_list = document.getElementById("panel_list");
  for (var i = options.length - 1; i >= 0; i--) {
    if (options[i].selected == true) {
      document.getElementById(options[i].dataset.origin_checkbox_id).checked = false;
      panel_list.remove(i);
    }
  }
}
document.getElementById("remove_panel").addEventListener('click', remove_panel);

// Save selected panels as file for download
function save_panels(event) {
  var panels_info = [];

  var selected_panels = document.getElementById("panel_list").options;
  for (var i = 0; i < selected_panels.length; i++) {
    panels_info.push(selected_panels[i].value);
  }

  var zeroes_filters = document.getElementsByClassName("zero_checkbox");
  for (var i = 0; i < zeroes_filters.length; i++) {
    if (zeroes_filters[i].checked){
      panels_info.push(zeroes_filters[i].value);
    }
  }

  var selected_time_interval =  "TIME," + document.getElementById('plot_time_interval').value.replace(" ", ",");
  panels_info.push(selected_time_interval);

  var blob = new Blob([panels_info.join("\n")], {type: "text/plain;charset=utf-8"});
  var url = URL.createObjectURL(blob);
  var a = document.createElement("a");
  a.href = url;
  a.download = "caa-panel-selection-" + get_timestamp() +".csv";
  a.click();
}
document.getElementById("save_panel_list").addEventListener('click', save_panels);

// Get a simple timestamp for file names
function get_timestamp() {
  return new Date().toISOString().slice(0, 19).replace("T", "").replace(/-/g, "").replace(/:/g, "");
}
window.get_timestamp = get_timestamp;

// Import panels selection from file
function import_panels(){
  document.getElementById('import_panels_file').click();
}
function load_panels_information(){
  document.getElementById("clear_panel_selection").click();
  var panel_checkboxes = document.getElementsByClassName("panel_checkbox");
  var zeroes_filters = document.getElementsByClassName("zero_checkbox");
  var file = document.getElementById('import_panels_file').files[0];
  var reader = new FileReader();
  reader.onload = function(event){
    var import_file_lines = event.target.result.split("\n");
    for (var i = 0; i < import_file_lines.length; i++) {
      var line = import_file_lines[i].trim();
      if (line.match(/^zero_/)) {
        for (var j = 0; j < zeroes_filters.length; j++) {
          if (zeroes_filters[j].value == line) {
            zeroes_filters[j].checked = true;
          }
        }
      } else if (line.match(/^TIME,/)) {
        var time_parts = line.split(",");
        var start_datetime = String(time_parts[1]);
        var stop_datetime = String(time_parts[2]);
        if (start_datetime.match(/^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$/) && stop_datetime.match(/^\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\dZ$/)) {
          document.getElementById('start_date').value = start_datetime.slice(0, 10);
          document.getElementById('start_time').value = start_datetime.slice(11, 19);
          document.getElementById('stop_date').value = stop_datetime.slice(0, 10);
          document.getElementById('stop_time').value = stop_datetime.slice(11, 19);
          sync_duration();
        }
      } else {
        for (var k = 0; k < panel_checkboxes.length; k++) {
          if (panel_checkboxes[k].dataset.panel_code == line) {
            panel_checkboxes[k].click();
          }
        }
      }
    }
  }
  reader.readAsText(file);
}
document.getElementById("import_panel_list").addEventListener('click', import_panels);
document.getElementById("import_panels_file").addEventListener('change', load_panels_information);

// Submit form with selected panels
var submit_plots_form = function(event) {
  hide_panels();
  show_loading_info();
  document.getElementById("plot_zeroes").value = "";
  var plot_panel_list = [];
  var panels = document.getElementById('panel_list').options;
	for (var i = 0; i < panels.length; i++) {
		plot_panel_list.push(panels[i].value);
  }
  document.getElementById("plot_panels").value = plot_panel_list.join(",");

  var zeroes = [];
  var zeroes_filters = document.getElementsByClassName("zero_checkbox");
  for (var i = 0; i < zeroes_filters.length; i++) {
    if (zeroes_filters[i].checked){
      zeroes.push(zeroes_filters[i].value);
    }
  }
  if (zeroes.length > 0) {
    document.getElementById("plot_zeroes").value = zeroes.join(",");
  }

  document.getElementById("plots_info").requestSubmit();
}
document.getElementById("submit_plots_info").addEventListener('click', function(event) { submit_plots_form(event) });
