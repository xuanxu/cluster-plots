require "open3"
require "oj"

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
    json_file = "test-#{rand(999999)}.json"

    pycom = [
      "python",
      "#{Rails.root}/libext/run_panel2.py",
      "-b", start_datetime,
      "-e", end_datetime,
      "-p", panels,
      "-j", json_file,
      "-o", "#{start_datetime}/#{end_datetime}"
    ]

    Rails.logger.info " * Running command: #{pycom.join(' ')}"
    stdout_str, stderr_str, status = Open3.capture3(*pycom)

    if Rails.env.development?
      Rails.logger.info "*************** DATA PROCESSING **************"
      Rails.logger.info "#{stdout_str}"
      Rails.logger.info "**********************************************"
      Rails.logger.info "#{stderr_str}"
      Rails.logger.info "**********************************************"
    end

    if status.success?
      Oj.load_file("#{Rails.root}/libext/results/json_charts/#{json_file}")
    else
      "Error #{stderr_str}"
    end
  end
end
