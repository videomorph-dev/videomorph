class VideoMorph < Formula
  include Language::Python::Virtualenv

  desc "Video Converter based on ffmpeg"
  homepage "https://github.com/videomorph-dev/videomorph/"
  url "https://github.com/videomorph-dev/videomorph/archive/master.zip", :using => :curl
  sha256 "85c2d58a63053614798a28b6d8a79c046cd3e29518174a364bd2e73b4e9d1f69"
  head "https://github.com/videomorph-dev/videomorph.git"

  # TODO: If you're submitting an existing package, make sure you include your
  #       bottle block here.

  depends_on "python"
  depends_on "ffmpeg"
  depends_on "pyqt"

  def install
    virtualenv_install_with_resources
    bin.install "setup.py"
  end

  # TODO: Add your package's tests here
end
