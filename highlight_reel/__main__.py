import argparse

from highlight_reel.clipper import process_files


def main():
    parser = argparse.ArgumentParser(description="Process and stitch video clips.")
    parser.add_argument(
        "--input_folder",
        type=str,
        default=".",
        help="Folder containing video files (default: '.')",
    )
    parser.add_argument(
        "--output_file",
        type=str,
        default="out.mp4",
        help="Output file name (default: 'out.mp4')",
    )
    parser.add_argument(
        "--clip_duration",
        type=float,
        default=3.0,
        help="Duration of each clip to extract in seconds (default: 3.0)",
    )
    parser.add_argument(
        "--skip_duration",
        type=float,
        default=7.0,
        help="Duration to skip forward in seconds (default: 7.0)",
    )
    args = parser.parse_args()

    process_files(
        input_folder=args.input_folder,
        output_file=args.output_file,
        clip_duration=args.clip_duration,
        skip_duration=args.skip_duration,
    )
