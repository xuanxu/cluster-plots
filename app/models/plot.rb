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
  attribute :data_error, :string

  def process_data
    if valid_params?
      call_csa
    else
      Rails.logger.error "Data validation error: #{data_error}"
      data_error
    end
  end

  private

  def call_csa
    return test_call if Rails.env.local?

    json_file = "data-#{Time.now.strftime(('%Y%m%d%H%M%S')) }#{rand(999999)}.json"

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
      Rails.logger.info "#{status.success? ? 'OK' : 'Failure'}"
      Rails.logger.info "**********************************************"
      Rails.logger.info "#{stdout_str}"
      Rails.logger.info "**********************************************"
    end

    if status.success?
      Oj.load_file("#{Rails.root}/libext/results/json_charts/#{json_file}")
    else
      Rails.logger.info "****** ERROR GETTING/PROCESSING DATA *********"
      Rails.logger.info "#{stderr_str}"
      Rails.logger.info "**********************************************"
      "Error getting/processing data from the Cluster Science Archive"
    end
  end

  def test_call
    Oj.load_file("#{Rails.root}/libext/results/json_charts/data-test.json")
  end

  def valid_params?
    if panels.blank?
      self.data_error = "No panels selected"
      return false
    end

    begin
      start_at = Time.parse(start_datetime)
      end_at = Time.parse(end_datetime)
    rescue ArgumentError
      self.data_error = "Invalid format for start or end datetime"
      return false
    end

    if start_at.nil? || end_at.nil?
      self.data_error = "Start and end datetime must have a value"
      return false
    end

    if start_at > end_at
      self.data_error = "Start datetime must be before end datetime"
      return false
    end

    if start_at == end_at
      self.data_error = "Time interval too short"
      return false
    end

    difference = end_at - start_at

    if panels.split(",").all? { |panel_name| panel_name.include?("_DM_") }  # Only Data Mining panels
      if difference.seconds.in_days > 31
        self.data_error = "For the Cluster Data Mining panels the time interval must be lower than 31 days"
        return false
      end
    else # Cluster or Double Star panels present
      if difference.seconds.in_hours > 57
        self.data_error = "Time interval must be less than 57 hours (one orbit) when panels from Cluster or Double Star are selected"
        return false
      end
    end

    true
  end
end
