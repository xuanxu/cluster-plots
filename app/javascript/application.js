// Configure your import map in config/importmap.rb. Read more: https://github.com/rails/importmap-rails
import "@hotwired/turbo-rails"
import "controllers"

// Apache ECharts library - load UMD build
// The UMD build will attach echarts to window.echarts automatically
import "echarts-umd"

// Ensure echarts is available globally
// Give it a moment to initialize
setTimeout(() => {
  if (!window.echarts) {
    console.error("ECharts failed to load");
  }
}, 0);

// Custom Cluster Plots files
import "custom/plots_form"

// Custom code to display charts
import "custom/chart-actions"
import "custom/charts"
import "@rails/request.js"
