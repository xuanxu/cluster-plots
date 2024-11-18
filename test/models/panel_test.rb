require "test_helper"

class PanelTest < ActiveSupport::TestCase
  test "panels data loaded" do
    assert_equal Panel.count, 368
  end
end
