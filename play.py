from natsort import natsorted
import os
import time
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Due to the fact commands can't take too many arguments, this program plays all the .txt files in a directory at the specified frame rate in order requiring little arguments.")
    parser.add_argument("frame_dir", help="Where to take the frames from")
    parser.add_argument("--fps", type=float, default=30, help="What FPS to play the frames at")

    args = parser.parse_args()

    frame_dir = str(args.frame_dir)
    fps = float(args.fps)

    for file in natsorted(os.listdir(frame_dir)):
        if not file.endswith(".txt"):
            continue

        with open(os.path.join(frame_dir, file), "rb") as f:
            sys.stdout.buffer.write(f.read())

        time.sleep(1/fps if fps != 0 else 0)

if __name__ == "__main__":
    main()
