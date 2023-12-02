from datetime import datetime
import piexif
import argparse
import os


def parse_args():
    # cli arguments
    parser = argparse.ArgumentParser(
        description="""
            Changes date taken exif data of photos in folder
            """
    )
    parser.add_argument("folder", help="full path of folder")
    parser.add_argument(
        "-d",
        "--date",
        help="date in this format dd/mm/yyyy",
        default=datetime.now().strftime("%d/%m/%Y"),
    )
    parser.add_argument(
        "-t",
        "--time",
        help="time in this format hh:mm:ss",
        default=datetime.now().strftime("%H:%M:%S"),
    )

    return parser.parse_args()


def set_date_taken(img, str_datetime=None):
    try:
        exif_dict = piexif.load(img)

        if not str_datetime:
            str_datetime = datetime.now().strftime("%Y:%m:%d %H:%M:%S")

        exif_dict["0th"][piexif.ImageIFD.DateTime] = str_datetime
        exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = str_datetime
        exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = str_datetime
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, img)

    except Exception as e:
        print(type(e).__name__, "-", e)


if __name__ == "__main__":
    args = parse_args()
    for filename in os.listdir(args.folder):
        date = datetime.strptime(args.date.strip(), "%d/%m/%Y").strftime("%Y:%m:%d")
        dt = f"{date} {args.time.strip()}"
        file = os.path.join(args.folder, filename)
        set_date_taken(file, dt)
