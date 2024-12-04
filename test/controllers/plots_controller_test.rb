require "test_helper"

class PlotsControllerTest < ActionDispatch::IntegrationTest
  test "should get index" do
    get plots_url
    assert_response :success
  end
end
