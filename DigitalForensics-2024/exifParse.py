#!/usr/bin/env python



import argparse
import sys
from exifread import process_file

class ImageMetadataProcessor:
    def __init__(self, filename):
        self.filename = filename
        self.data = None
        self.date_time = None
        self.zone = None
        self.angle = None
        self.heading = ['Make', 'Model', 'DateTime', 'GPSLatitude', 'GPSLongitude']



    def load_metadata(self):
        try:
            with open(self.filename, 'rb') as file:
                self.data = process_file(file)
        except FileNotFoundError:
            print("Error! - File Not Found!")
            sys.exit(1)

    def display_info(self):
        print("Source File: " + self.filename)

    def process_image_tags(self):
        tags = list(self.data.keys())
        for tag in tags:
            if 'Image' in tag and tag[6:] in self.heading:
                if tag[6:] == 'DateTime':
                    self.date_time = self.data[tag].printable
                else:
                    print(f"{tag[6:]}: {self.data[tag].printable}")
        
        if self.date_time:
            print(f"Original Date/Time: {self.date_time}")

    def process_gps_tags(self):
        tags = list(self.data.keys())
        for tag in tags:
            if 'GPS' in tag:
                if tag[4:] == 'GPSLatitudeRef':
                    self.zone = self.data[tag].printable
                if tag[4:] == 'GPSLongitudeRef':
                    self.angle = self.data[tag].printable

    def print_gps_info(self):
        tags = list(self.data.keys())
        for tag in tags:
            if 'GPS' in tag and tag[4:] in self.heading:
                dir_values = self.data[tag].printable.strip('][').split(', ')
                degrees, minutes, seconds = ImageMetadataProcessor.parse_coordinates(dir_values)
                prefix = "-" if (tag[4:] == 'GPSLatitude' and self.zone == 'S') or (tag[4:] == 'GPSLongitude' and self.angle == 'W') else ""
                print(f"{tag[7:]}: {prefix}{degrees} degrees, {minutes} minutes, {seconds} seconds")

 

    def parse_coordinates(dir_values):
        degrees = dir_values[0]
        minutes = float(dir_values[1].split('/')[0]) / float(dir_values[1].split('/')[1]) if '/' in dir_values[1] else float(dir_values[1])
        seconds = float(dir_values[2].split('/')[0]) / float(dir_values[2].split('/')[1]) if '/' in dir_values[2] else float(dir_values[2])
        return degrees, minutes, seconds



def main():
    parser = argparse.ArgumentParser(description='Process image metadata ')
    parser.add_argument('image', metavar='IMG', type=str, nargs='?', help='image file to procss')
    args = parser.parse_args()

    if args.image is None:
        print("Error! - No Image File Specified!")
        sys.exit(1)

    processor = ImageMetadataProcessor(args.image)
    processor.load_metadata()
    processor.display_info()
    processor.process_image_tags()
    processor.process_gps_tags()
    processor.print_gps_info()


if __name__ == '__main__':
    main()
