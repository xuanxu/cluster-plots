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
  if (panels_listings.style.display === "none") {
    panels_listings.style.display = "block";
    panels_heading.innerHTML = "Panel selection <i class='fa fa-caret-down'></i>"
  } else {
    panels_listings.style.display = "none";
    panels_heading.innerHTML = "Show panel selection <i class='fa fa-caret-right'></i>"
  }
}
document.getElementById("panels_heading").addEventListener('click', toggle_panels);

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
  stop.setDate(stop.getDate() + parseInt(duration_days.value));
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
