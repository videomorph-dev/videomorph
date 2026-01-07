class Videomorph < Formula
  include Language::Python::Virtualenv

  desc "Video Converter based on ffmpeg, Python, and Qt6"
  homepage "https://github.com/videomorph-dev/videomorph"
  url "https://github.com/videomorph-dev/videomorph/archive/refs/tags/v1.6.0.tar.gz"
  sha256 "85c2d58a63053614798a28b6d8a79c046cd3e29518174a364bd2e73b4e9d1f69"
  license "Apache-2.0"
  head "https://github.com/videomorph-dev/videomorph.git", branch: "master"

  depends_on "python@3.12"
  depends_on "pyqt@6"
  depends_on "ffmpeg"

  def install
    virtualenv_install_with_resources

    # Install shared resources (profiles, translations, sounds, docs)
    pkgshare.install Dir["share/videomorph/*"]
    doc.install Dir["share/doc/videomorph/*"]
    man1.install "share/man/man1/videomorph.1"
  end

  def caveats
    <<~EOS
      VideoMorph requires ffmpeg to be installed and available in your PATH.
      ffmpeg was installed as a dependency.

      To launch VideoMorph, run:
        videomorph
    EOS
  end

  test do
    # Test that the package can be imported
    system Formula["python@3.12"].opt_bin/"python3", "-c", "import videomorph"

    # Test that the entry point script exists and is executable
    assert_predicate bin/"videomorph", :exist?
    assert_predicate bin/"videomorph", :executable?

    # Test version output (if supported) or basic help
    assert_match "videomorph", shell_output("#{bin}/videomorph --help 2>&1", 0)
  end
end
