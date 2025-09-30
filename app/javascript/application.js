// Configure your import map in config/importmap.rb. Read more: https://github.com/rails/importmap-rails
import "@hotwired/turbo-rails"
import "controllers"

// Apache ECharts library
import * as echarts from "echarts"
window.echarts = echarts;

// Custom Cluster Plots files
import "custom/plots_form"

// Custom code to display charts
import "custom/chart-actions"
import "custom/charts"
import "@rails/request.js"
