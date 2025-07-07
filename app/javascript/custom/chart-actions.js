function manageBorder(action="show") {
  const borderable_charts = window.all_charts["plot_charts"] || [];
  const border_width = action === "show" ? 1 : 0;
  for (var i = 0; i < borderable_charts.length; i++) {
    borderable_charts[i].update({chart: { borderWidth: border_width }});
  }
}
