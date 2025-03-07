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

    @p = panels.split(",")

    @plot = Plot.new(start_datetime: start_datetime, end_datetime: end_datetime, panels: panels)
    @plot_info = @plot.call_csa


    if @plot.ready?
      render :show
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
end
