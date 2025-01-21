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
    @cluster_panels = Panel.ready.by_mission("cluster")
    @double_star_panels = Panel.ready.by_mission("double_star")
    @data_mining_panels = Panel.ready.by_mission("data_mining")
  end
end
