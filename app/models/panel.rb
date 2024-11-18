class Panel < ApplicationRecord
  validates_uniqueness_of :name, scope: [:mission]
end
