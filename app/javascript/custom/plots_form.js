// Update plot times
function update_plot_times() {
  var plot_times = document.getElementById("plot_times");
  var start_date = document.getElementById("start_date");
  var start_time = document.getElementById("start_time");
  var stop_date = document.getElementById("stop_date");
  var stop_time = document.getElementById("stop_time");
  plot_times.innerHTML = start_date.value + "T" + start_time.value + "Z " + stop_date.value + "T" + stop_time.value + "Z";
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
