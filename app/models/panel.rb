class Panel < ApplicationRecord
  enum :mission, cluster: 1, double_star: 2, data_mining: 3
  validates_uniqueness_of :name, scope: :mission
end
