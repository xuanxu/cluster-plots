class PlotsController < ApplicationController
  before_action :load_panels

  def index
  end

  def new
  end

  def show
    if @plot.nil?
      redirect_to new_plot_path
    end
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
    file_list = cef_files_params[:cefs].split(",").map(&:strip)
    times = cef_files_params[:times].to_s.strip.gsub(/\D/, "")

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

  def spacecraft_info
    data = Plot.new.spacecraft_data(spacecraft_info_params)

    if data.is_a?(String)
      reply = { status: "Error", info: data }
    else
      reply = { status: "OK", info: data.to_json }
    end

    render json: reply
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

  def cef_files_params
    params.permit(:cefs, :times)
  end

  def spacecraft_info_params
    params.require(:spacecraft_info).permit(:mission, :spacecraft, :start_at, :end_at, info_list: [], time_ticks: [])
  end
end
