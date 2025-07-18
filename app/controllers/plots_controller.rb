class PlotsController < ApplicationController
  before_action :load_panels

  def index
  end

  def new
  end

  def generate
    panels = plot_params[:panels]
    time_interval = plot_params[:time_interval]

    start_datetime, end_datetime = time_interval.split(" ")
    @start_date, @start_time = start_datetime.split("T")
    @stop_date, @stop_time = end_datetime.split("T")

    @p = panels.split(",").map(&:strip)

    @plot = Plot.new(start_datetime: start_datetime, end_datetime: end_datetime, panels: @p.join(","))
    @plot_info = @plot.process_data

    render :show
  end

  def cef_files
    file_list = params[:cefs].split(",").map(&:strip)
    times = params[:times].to_s.strip.gsub(/\D/, "")

    if file_list.empty?
      send_data '{"error": "No files available, try replotting"}', filename: "error_retrieving_cef_files.json", type: "application/json", disposition: "attachment"
      return
    end

    begin
      send_data ZipCefFiles.zip_cef_data(file_list), filename: "cef_files_#{times}.zip", type: "application/zip", disposition: "attachment"
    rescue ZipCefFiles::Error => e
      send_data '{"error": "' + e.message + '"}', filename: "error_retrieving_cef_files.json", type: "application/json", disposition: "attachment"
    rescue
      send_data '{"error": "Error generating the zip file, please try again later"}', filename: "error_retrieving_cef_files.json", type: "application/json", disposition: "attachment"
    end
  end

  def show
    if @plot.nil?
      redirect_to new_plot_path
    end
  end

  private
  def load_panels
    @cluster_panels_by_instrument = Panel.ready.by_mission("cluster").to_a.group_by { |panel| panel.experiment }
    @double_star_panels_by_instrument = Panel.ready.by_mission("double_star").to_a.group_by { |panel| panel.experiment }
    @data_mining_panels_by_instrument = Panel.ready.by_mission("data_mining").to_a.group_by { |panel| panel.experiment }
  end

  def plot_params
    params.require(:plot).permit(:panels, :time_interval)
  end

  def def_files_params
    params.require(:cefs, :times)
  end
end
