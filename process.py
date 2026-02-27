from itertools import zip_longest
from PIL import Image
from natsort import natsorted
import multiprocessing
import argparse
import glob
import os
import functools

class GenerateSettings:
    width: int
    height: int
    color: bool

def generate_image_lines(settings: GenerateSettings, verbose: bool, filename: str) -> tuple[tuple[str, list[str]], list[tuple[str, str]]]:
    img = Image.open(filename)
    img = img.resize((settings.width, settings.height))


    width, height = img.size

    if verbose:
        print(filename)

    video_lines = []
    for y in range(height):
        row = ""
        last_color = None
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            color = (r, g, b)
            if settings.color:
                if color != last_color:
                    row += f"\033[38;2;{r};{g};{b}m"
                    last_color = color

                row += "@"
            else:
                brightness = (r + g + b) / 3
                brightness_chars = " .*:$@"
                row += brightness_chars[round((brightness / 255) * (len(brightness_chars)-1))]

        if settings.color:
            row += "\033[0m"

        video_lines.append(row)

    sample_files = []

    return ((filename, video_lines), sample_files)

def main():
    parser = argparse.ArgumentParser(
        description="Processes image sequences into frames that can be catted as ACII when cat in order")
    parser.add_argument("frame_dir", help="Where to take the .png's from and put the .txt files at")
    parser.add_argument("--width", type=int, default=192, help="The width to scale to")
    parser.add_argument("--height", type=int, default=48, help="The height to scale to")
    parser.add_argument("--color", action="store_true", help="Display color using ANSI instead of black and white")

    parser.add_argument("--jobs", "-j", type=int, default=1, help="The amount of jobs to use to generate the frames")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose mode")

    args = parser.parse_args()

    frame_dir = str(args.frame_dir)

    width = int(args.width)
    height = int(args.height)
    color = bool(args.color)

    verbose = bool(args.verbose)
    jobs = int(args.jobs)

    settings = GenerateSettings()
    settings.width = width
    settings.height = height
    settings.color = color

    image_gen_func = functools.partial(generate_image_lines, settings, verbose)

    with multiprocessing.Pool(jobs) as p:
        last_image_lines = []
        for (image_file, image_lines), audio_frames in p.imap(image_gen_func, natsorted(glob.glob(os.path.join(frame_dir, "*.png")))):
            with open(image_file + ".txt", "w") as f:
                changes = {}
                for i, (old_line, new_line) in enumerate(zip_longest(last_image_lines, image_lines)):
                    if old_line != new_line:
                        changes[i + 1] = new_line or " " * width

                if len(last_image_lines) == 0:
                    for _ in range(height - 1):
                        f.write(" " * width)
                        f.write("\n")

                buffer = []
                cursor_pos = height

                for line, new_line in sorted(changes.items(), reverse=True):
                    move_up = cursor_pos - line
                    if move_up > 0:
                        buffer.append(f"\033[{move_up}A\r\033[2K{new_line}")
                    else:
                        buffer.append(f"\r\033[2K{new_line}")
                    cursor_pos = line

                if cursor_pos < height:
                    buffer.append(f"\033[{height - cursor_pos}B")

                f.write("".join(buffer))
                last_image_lines = image_lines

            for (audio_file, audio_data) in audio_frames:
                with open(audio_file + ".txt", "w") as f:
                    f.write(audio_data)

if __name__ == "__main__":
    main()
