"""This module provides tests for probe.py module."""

from videomorph.converter.probe import Probe


class TestProbe:
    """Class for testing probe.py module."""

    def test_format_info(self) -> None:
        assert Probe("sample-video.mp4").format_info == {
            "filename": "sample-video.mp4",
            "nb_streams": "2",
            "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
            "format_long_name": "QuickTime / MOV",
            "duration": "57.516009",
            "size": "5329356",
            "bit_rate": "741269",
        }

    def test_video_info(self) -> None:
        assert Probe("sample-video.mp4").video_info == {
            "codec_name": "h264",
            "codec_long_name": "H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10",
            "width": "854",
            "height": "480",
            "bit_rate": "669499",
        }

    def test_audio_info(self) -> None:
        assert Probe("sample-video.mp4").audio_info == {
            "codec_name": "aac",
            "codec_long_name": "AAC (Advanced Audio Coding)",
        }

    def test_subtitle_info(self) -> None:
        assert Probe("sample-video.mp4").subtitle_info == {}
