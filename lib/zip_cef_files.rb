require "zip"
require "tempfile"

module ZipCefFiles

  class Error < StandardError; end

  CEF_FILES_PATH = File.join(Rails.root, "libext", "results", "cef_files")

  def self.zip_cef_data(cef_file_names = [])
    cef_file_names = cef_file_names.compact_blank
    cef_file_names.map! { |name| name.strip.gsub(/[^A-Za-z0-9_.]/, "") }

    unless cef_file_names.any? { |filename| File.exist?(File.join(CEF_FILES_PATH, filename)) }
      raise ZipCefFiles::Error, "Temporary CEF files created for these plots are not available anymore (they are keep for 24h), try regenerating the plots"
    end

    begin
      zip_file = Tempfile.new("cefs_#{rand(9999999)}.zip")

      Zip::File.open(zip_file.path, Zip::File::CREATE) do |zipfile|
        cef_file_names.each do |cef_file_name|
          cef_files_path = File.join(CEF_FILES_PATH, cef_file_name)
          zipfile.add(cef_file_name, cef_files_path) if File.exist?(cef_files_path)
        end
      end

      zip_data = File.read(zip_file.path)
    ensure
      zip_file.close
      zip_file.unlink
    end
  end
end
