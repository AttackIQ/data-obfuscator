#!/usr/bin/env python3
import argparse
from bitstring import BitArray
from hashlib import md5
from os import path
from PIL import Image


PATH = path.dirname(path.realpath(__file__))
JPEG_HEADER = b"\xff\xd8\xff\xe0\x00\x10\x4a\x46\x49\x46\x00\x01"
APPEND_FILE_MARKER = md5(b'<AttackIQ - Start of Appended File>').digest()
LSB_PAYLOAD_LENGTH_BITS = 32


def obfuscate_via_header(data_file, output_file):
    jpeg_header = bytes(JPEG_HEADER)
    data = read_data(data_file)
    write_data(output_file, jpeg_header + data)


def deobfuscate_via_header(input_file, output_file):
    data = read_data(input_file)
    write_data(output_file, data[12:])


def obfuscate_via_append(data_file, input_file, output_file):
    data = read_data(data_file)
    input_file_data = read_data(input_file)
    write_data(output_file, input_file_data + APPEND_FILE_MARKER + data)


def deobfuscate_via_append(input_file, output_file):
    data = read_data(input_file)
    file_start = data.find(APPEND_FILE_MARKER)
    write_data(output_file, data[file_start+len(APPEND_FILE_MARKER):])


def obfuscate_via_lsb(data_file, input_file, output_file):
    data = read_data(data_file)
    data = BitArray(uint=len(data) * 8, length=LSB_PAYLOAD_LENGTH_BITS).bin + BitArray(bytes=data).bin

    i = 0
    try:
        with Image.open(input_file) as img:
            width, height = img.size
            if len(data) > width * height * 3:
                print("Data is too large to be embedded in the image. Data contains {} bytes, maximum is {}".format(
                    int(len(data) / 8), int(width * height * 3 / 8)))
                exit(1)
            for x in range(0, width):
                for y in range(0, height):
                    pixel = list(img.getpixel((x, y)))
                    for n in range(0, 3):
                        if i < len(data):
                            pixel[n] = pixel[n] & ~1 | int(data[i])
                            i += 1
                    img.putpixel((x, y), tuple(pixel))
                    if i >= len(data):
                        break
                if i >= len(data):
                    break
            img.save(output_file, "png")
    except IOError:
        print("Could not open {}. Check that the file exists and it is a valid image file.".format(input_file))
        exit(1)
    print("Data written to {}".format(output_file))


def deobfuscate_via_lsb(input_file, output_file):
    try:
        with Image.open(input_file) as img:
            payload_length = int("".join([str(x) for x in decode_img_nbits(img, LSB_PAYLOAD_LENGTH_BITS)]), 2)
            data = decode_img_nbits(img, payload_length + LSB_PAYLOAD_LENGTH_BITS)[LSB_PAYLOAD_LENGTH_BITS:]
            data = BitArray(bin="".join([str(x) for x in data])).bytes
    except IOError:
        print("Could not open {}".format(input_file))
        exit(1)
    write_data(output_file, data)


def decode_img_nbits(img, nbits):
    data = []
    i = 0
    width, height = img.size
    for x in range(0, width):
        for y in range(0, height):
            pixel = list(img.getpixel((x, y)))
            for n in range(0, 3):
                if i < nbits:
                    data.append(pixel[n] & 1)
                    i += 1
            if i >= nbits:
                break
        if i >= nbits:
            break
    return data


def read_data(input_file):
    try:
        with open(input_file, "rb") as f:
            data = f.read()
    except IOError:
        print("Could not open file {}".format(input_file))
        exit(1)
    return data


def write_data(output_file, data):
    try:
        with open(output_file, "wb") as f:
            f.write(data)
    except IOError:
        print("Could not open file {}".format(output_file))
        exit(1)
    print("Data written to {}".format(output_file))


def parse_args():
    parser = argparse.ArgumentParser(description='Data Obfuscator')
    parser.add_argument('action', metavar='action', choices=['obfuscate', 'deobfuscate'], type=str,
                        help='Action to do (obfuscate or deobfuscate data)')
    parser.add_argument('-d', '--data', metavar='data', type=str, help='Data to be obfuscated (required if action is '
                                                                       '"obfuscate")', required=False)
    parser.add_argument('-i', '--input', metavar='input', type=str,
                        help="Image where the data will be hidden (if action is \"obfuscate\") or from where the data "
                             "will be extracted (if method is \"deobfuscate\"). Required if action is \"deobfuscate\"."
                             "If action is \"obfuscate\", it will only be used in append and LSB methods "
                             "(default is a blank image)",
                        required=False)
    parser.add_argument('-o', '--output', metavar='output', type=str, help="Name of the output file", required=False)
    parser.add_argument('-m', '--method', choices=['header', 'append', 'lsb'], metavar='method', type=str,
                        help='Obfuscation/deobfuscation method. Valid options: header, append, lsb', required=True)

    args = parser.parse_args()
    extension = 'png' if args.method == 'lsb' else 'jpg'
    # Further parameter validation
    if args.action == 'obfuscate':
        if args.method == 'header' and args.input:
            print("Method 'header' does not take any input file. Input file {} will be ignored".format(args.input))
        if not args.data:
            print("Parameter -d/--data is required for the obfuscate method\n")
            parser.print_help()
            exit(1)
    if args.action == 'deobfuscate':
        if not args.input:
            print("Parameter -i/--input is required for the deobfuscate method\n")
            parser.print_help()
            exit(1)
    if not args.output:
        if args.action == 'obfuscate':
            args.output = '{}-{}.{}'.format(path.splitext(args.data)[0], args.method, extension)
        else:
            args.output = '{}-{}'.format(path.splitext(args.input)[0], 'recovered')
    if not args.input:
        args.input = path.join(PATH, 'defaults/blank-big.jpg') if args.method == 'lsb' \
            else path.join(PATH, 'defaults/blank.jpg')

    return args


if __name__ == "__main__":
    args = parse_args()

    if args.action == 'obfuscate':
        if args.method == 'header':
            obfuscate_via_header(data_file=args.data, output_file=args.output)
        elif args.method == 'append':
            obfuscate_via_append(data_file=args.data, input_file=args.input, output_file=args.output)
        elif args.method == 'lsb':
            obfuscate_via_lsb(data_file=args.data, input_file=args.input, output_file=args.output)
    else:
        if args.method == 'header':
            deobfuscate_via_header(input_file=args.input, output_file=args.output)
        elif args.method == 'append':
            deobfuscate_via_append(input_file=args.input, output_file=args.output)
        elif args.method == 'lsb':
            deobfuscate_via_lsb(input_file=args.input, output_file=args.output)
