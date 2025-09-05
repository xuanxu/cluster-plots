require "test_helper"
require "open3"

class LibextCallsTest < ActiveSupport::TestCase
  test "calling run_panel2" do
    pycom =<<-PYPLOT
    python #{Rails.root}/libext/run_panel2.py -b '2016-09-11T00:00:00Z' -e '2016-09-11T01:15:00Z' -p 'C4_CG_CIS_NI_CAA' -n 'test.ps' -t 'highcharts' -j 'testC42016X.json' -o '2016-09-11T00:00:00Z/2016-09-11T01:15:00Z'
    PYPLOT

    stdout_str, stderr_str, status = Open3.capture3 pycom
    assert_not stderr_str.include?("ModuleNotFoundError"), "Missing module: \n\n #{stderr_str}"
    assert status.success?, "Failed to run run_panel2.py: \n\n #{stderr_str}"
  end
end
