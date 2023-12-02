from datetime import datetime, timedelta
import piexif
import argparse
import os
import re


def main():
    args = parse_args()

    for filename in os.listdir(args.folder):
        file = os.path.join(args.folder, filename)

        if args.offset:
            set_date_taken(file, offset=args.offset.strip())
        else:
            date = datetime.strptime(args.date.strip(), "%d/%m/%Y").strftime("%Y:%m:%d")
            dt = f"{date} {args.time.strip()}"
            set_date_taken(file, dt)


def set_date_taken(img, str_datetime=None, offset=None):
    """
    Modify the image's (`img`) exif dates to `str_datetime` or adjust existing dates
    by the `offset` value (if specified)
    """
    try:
        exif_dict = piexif.load(img)
    except Exception as e:
        print(type(e).__name__, "-", e)
        return

    # default value for str_datetime
    if not str_datetime:
        str_datetime = datetime.now().strftime("%Y:%m:%d %H:%M:%S")

    # calculate new datetime if using offset
    if offset:
        # get date from exif
        exif_date = exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
        try:
            exif_date = datetime.strptime(exif_date.decode(), "%Y:%m:%d %H:%M:%S")
        except:
            exif_date = datetime.strptime(exif_date, "%Y:%m:%d %H:%M:%S")

        # create timedelta object from offset
        n, units = parse_offset(offset)
        if units == "d":
            delta = timedelta(days=n)
        elif units == "h":
            delta = timedelta(hours=n)
        elif units == "m":
            delta = timedelta(minutes=n)

        str_datetime = (exif_date + delta).strftime("%Y:%m:%d %H:%M:%S")

    # modify exif dates on image
    exif_dict["0th"][piexif.ImageIFD.DateTime] = str_datetime
    exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal] = str_datetime
    exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized] = str_datetime
    exif_bytes = piexif.dump(exif_dict)
    piexif.insert(exif_bytes, img)


def parse_offset(offset):
    """
    Parses the number `n` and `units` d, h, or m (days, hours, minutes respectively)
    from the `offset` string provided.

    `offset` is expected as a positive or negative number followed by `d`, `h` or `m`.
        (eg. `+3d`, `-2h`, `-30m`, etc).
    """
    pattern = r"(\+|-)?(\d+)(d|h|m)"

    if m := re.search(pattern, offset, re.IGNORECASE):
        plus_minus = "+" if m.group(1) == None else m.group(1)
        value = m.group(2)
        units = m.group(3).lower()

        if plus_minus == "+":
            n = int(value)
        elif plus_minus == "-":
            n = int(value) * -1
        else:
            raise ValueError

        return n, units

    return None, None


def parse_args():
    # cli arguments
    parser = argparse.ArgumentParser(
        description="Modifies date metadata of photos in a folder."
    )
    parser.add_argument(
        "folder",
         help="full path of folder"
    )
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
    parser.add_argument(
        "-o",
        "--offset",
        help='if adjusting by offset eg "+2h", "-1d", "+30m", etc',
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
