class Plot
  include ActiveModel::Model

  attribute :start_time, :datetime
  attribute :end_time, :datetime
  attribute :panels, :string
  attribute :json_file, :string
  attribute :mission, :string
end
