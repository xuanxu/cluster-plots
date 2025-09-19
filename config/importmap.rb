# Pin npm packages by running ./bin/importmap

pin "application"
pin "@hotwired/turbo-rails", to: "turbo.min.js"
pin "@hotwired/stimulus", to: "stimulus.min.js"
pin "@hotwired/stimulus-loading", to: "stimulus-loading.js"
pin_all_from "app/javascript/controllers", under: "controllers"
pin_all_from "app/javascript/custom", under: "custom"
pin "highcharts/highcharts"
pin "highcharts/heatmap"
pin "highcharts/exporting"
pin "highcharts/offline-exporting"
pin "highcharts/export-data"
pin "highcharts/accessibility"
