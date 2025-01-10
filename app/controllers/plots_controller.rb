class PlotsController < ApplicationController
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
end
