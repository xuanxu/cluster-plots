require "open3"

class Plot
  include ActiveModel::Model
  include ActiveModel::Attributes

  attribute :start_datetime, :string
  attribute :end_datetime, :string
  attribute :panels, :string
  attribute :json_file, :string
  attribute :mission, :string

  def ready?
    true
  end

  def call_csa
    pycom =<<-PYPLOT
    python #{Rails.root}/libext/run_panel2.py -b '#{start_datetime}' -e '#{end_datetime}' -p '#{panels}' -n 'test.ps' -t 'highcharts' -c 1 -j 'test-#{rand(999999)}.json' -o '#{start_datetime}/#{end_datetime}'
    PYPLOT

    stdout_str, stderr_str, status = Open3.capture3 pycom

    if status.success?
      stdout_str
    else
      "Error #{stderr_str}"
    end
  end
end
