class PlotsController < ApplicationController
  before_action :load_panels

  def index
  end

  def new
  end

  def generate
    @plot = Plot.new()

    if @plot.ready?
      render :show
    end
  end

  private
  def load_panels
    @cluster_panels_by_instrument = Panel.ready.by_mission("cluster").to_a.group_by { |panel| panel.experiment }
    @double_star_panels_by_instrument = Panel.ready.by_mission("double_star").to_a.group_by { |panel| panel.experiment }
    @data_mining_panels_by_instrument = Panel.ready.by_mission("data_mining").to_a.group_by { |panel| panel.experiment }
  end
end
