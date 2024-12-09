import os
import subprocess

from dateutil.parser import parse
from moviepy import VideoFileClip, concatenate_videoclips


def get_creation_time(video_path):
    """Extract the creation time of a video using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-print_format",
                "json",
                "-show_format",
                video_path,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        metadata = result.stdout
        # Look for 'creation_time' in the metadata
        for line in metadata.splitlines():
            if '"com.apple.quicktime.creationdate"' in line:
                raw_time = (
                    line.split(": ", 1)[1].strip().strip('"').strip(",").rstrip('"')
                )
                print(raw_time)
                sanitized_time = raw_time.replace(
                    "Z", "+00:00"
                )  # Replace 'Z' with UTC offset
                return parse(sanitized_time)  # Robust parsing of ISO string
    except Exception as e:
        print(f"Error extracting creation time for {video_path}: {e}")
    return None


def sort_videos_by_creation_time(video_files):
    """Sort video files by their creation time."""
    videos_with_time = [(video, get_creation_time(video)) for video in video_files]
    # Sort by creation_time (fall back to name if time is None)
    return [video for video, _ in sorted(videos_with_time, key=lambda x: x[1])]


def get_video_properties(video_path):
    """Extract properties of a video file: resolution, format."""
    clip = VideoFileClip(video_path)
    return {
        "resolution": clip.size,
        "format": clip.filename.split(".")[-1].lower(),
    }


def find_lowest_resolution(video_files):
    """Determine the lowest resolution among all video files."""
    resolutions = [get_video_properties(video)["resolution"] for video in video_files]
    return min(resolutions, key=lambda res: res[0] * res[1])  # Compare by total pixels


def process_video(video_path, clip_duration, skip_duration, target_resolution):
    """Extract clips from the video, resizing to the target resolution."""
    clip = VideoFileClip(video_path)
    if clip.size != target_resolution:
        clip = clip.resized(new_size=target_resolution)  # Resize to target resolution

    subclips = []
    duration = clip.duration
    current_time = 0

    while current_time + clip_duration <= duration:
        subclips.append(clip.subclipped(current_time, current_time + clip_duration))
        current_time += clip_duration + skip_duration

    return subclips


def process_files(input_folder, output_file, clip_duration, skip_duration):
    # Get all video files from the input folder
    video_files = sorted(
        [
            os.path.join(input_folder, f)
            for f in os.listdir(input_folder)
            if f.lower().endswith((".mp4", ".mov", ".avi", ".mkv"))
        ]
    )
    if not video_files:
        raise ValueError("No video files found in the specified folder.")

    # Sort files by creation date/time
    video_files = sort_videos_by_creation_time(video_files)
    print("Sorted video files:", video_files)

    # Determine the lowest resolution for normalization
    target_resolution = find_lowest_resolution(video_files)
    print(f"Normalizing all videos to resolution: {target_resolution}")

    # Process all videos and collect subclips
    all_clips = []
    for video in video_files:
        print(f"Processing video: {video}")
        all_clips.extend(
            process_video(video, clip_duration, skip_duration, target_resolution)
        )

    # Concatenate all subclips into a single video
    final_video = concatenate_videoclips(all_clips, method="compose")
    final_video.write_videofile(output_file, codec="libx264", audio_codec="aac")
    print(f"Video created: {output_file}")


# Example usage
if __name__ == "__main__":
    process_files(
        input_folder="./input_videos",
        output_file="output_video.mp4",
        clip_duration=3,
        skip_duration=7,
    )
