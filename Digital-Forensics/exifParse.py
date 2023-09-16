#!/usr/bin/env python

import argparse
import sys
from exifread import process_file, exif_log


def main():
    parser = argparse.ArgumentParser(description='Process image metadata')
    parser.add_argument('image', metavar='IMG', type=str, nargs='?', help='image file to process')
    args = parser.parse_args()

    if args.image is None:
        print("Error! - No Image File Specified!")
        sys.exit()

    try:
        with open(args.image, 'rb') as file:
            data = process_file(file)
            tags = list(data.keys())
            tags.sort()
            print("Source File:", args.image)

            heading = ['Make', 'Model', 'DateTime', 'GPSLatitude', 'GPSLongitude']
            date_time = None
            zone = None
            angle = None

            for i in tags:
                try:
                    if ('Image' in i):
                        if(i[6:] in heading and i[6:] == 'DateTime'):
                            date_time = data[i].printable
                        elif(i[6:] in heading):
                            print(i[6:], ": ", data[i].printable, sep='')
                except Exception:
                    print("{}: {}".format(i, str(data[i])))

            if date_time is not None:
                print("Original Date/Time:", date_time)

            for i in tags:
                try:
                    if ('GPS' in i):
                        if(i[4:] == 'GPSLatitudeRef'):
                            zone = data[i].printable
                        if(i[4:] == 'GPSLongitudeRef'):
                            angle = data[i].printable
                except Exception:
                    print("{}: {}".format(i, str(data[i])))

            for i in tags:
                try:
                    if ('GPS' in i and i[4:] in heading):
                        data_dir = data[i].printable.strip('][').split(', ')
                        nums = data_dir[2].split('/')
                        char = float(nums[0])/float(nums[1]) if len(nums) > 1 else 0
                        num = data_dir[1].split('/')
                        var = float(num[0])/float(num[1]) if len(num) > 1 else 0

                    if((i[4:] == 'GPSLatitude' and zone == 'S') or (i[4:] == 'GPSLongitude' and angle == 'W')):
                        if (char != 0 and var == 0): 
                            print(i[7:], ": -", data_dir[0], " degrees, ", float(data_dir[1])," minutes, ", char," seconds", sep='')
                        elif (char != 0 and var != 0):
                            print(i[7:], ": -", data_dir[0], " degrees, ", float(var)," minutes, ", char," seconds", sep='')
                        elif (char == 0 and var != 0):
                            print(i[7:], ": -", data_dir[0], " degrees, ", float(var)," minutes, ", data_dir[2]," seconds", sep='')
                        else:
                            print(i[7:], ": -", data_dir[0], " degrees, ", float(data_dir[1])," minutes, ", data_dir[2]," seconds", sep='')

                    elif((i[4:] == 'GPSLatitude' and zone == 'N') or (i[4:] == 'GPSLongitude' and angle == 'E')):                           
                        if (char != 0 and var == 0): 
                            print(i[7:], ": ", data_dir[0], " degrees, ", float(data_dir[1])," minutes, ", char," seconds", sep='')
                        elif (char != 0 and var != 0):
                            print(i[7:], ": ", data_dir[0]," degrees, ", float(var)," minutes, ", char," seconds", sep='')
                        elif (char == 0 and var != 0):
                            print(i[7:], ": ", data_dir[0], " degrees, ", float(var)," minutes, ", data_dir[2]," seconds", sep='')
                        else:
                            print(i[7:], ": ", data_dir[0], " degrees, ", float(data_dir[1])," minutes, ", data_dir[2]," seconds", sep='')

                except Exception:
                    print("%s : %s", i, str(data[i]))

    except FileNotFoundError:
        print("Error! - File Not Found!")

if __name__ == '__main__':
	main()


#Sources Consulted:
#https://www.geeksforgeeks.org/python-sep-parameter-print/
#https://pypi.org/project/exif/
#https://medium.com/spatial-data-science/how-to-extract-gps-coordinates-from-images-in-python-e66e542af354
