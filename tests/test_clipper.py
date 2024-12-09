from highlight_reel.clipper import get_video_properties

def test_get_video_properties():
    # Example test to validate video properties
    video_path = "tests/test_video.mp4"
    properties = get_video_properties(video_path)
    assert "fps" in properties
    assert "resolution" in properties
    assert "format" in properties