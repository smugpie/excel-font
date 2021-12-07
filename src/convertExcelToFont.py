#!/usr/bin/python3
import sys
import getopt
from shutil import rmtree
from drawing import draw_pixel
from utils import index_contains
from fontTools import agl
from fontParts.world import *
from fontmake import font_project
import pandas


def main(argv):
    input_file = ''
    output_file = ''
    font_format = ''
    font_name = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:f:n:",["input_file=","output_file=","format=","name="])
    except getopt.GetoptError:
        print('Usage: openAmigaFont.py -i <inputfile> -o <outputfile> -f <format> -n <name>')
        print('where format is one of ufo, ttf, otf')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print('Usage: openAmigaFont.py -i <inputfile> -o <outputfile> -f <format> -n <name>')
            print('where format is one of ufo, ttf, otf')
            sys.exit()
        elif opt in ("-i", "--input_file"):
            input_file = arg
        elif opt in ("-o", "--output_file"):
            output_file = arg
        elif opt in ("-f", "--format"):
            font_format = arg
            if font_format not in ('ufo', 'ttf', 'otf'):
                print('Format must be one of ufo, ttf, otf')
                sys.exit(2)
        elif opt in ("-n", "--name"):
            font_name = arg

    if input_file == '':
        print('Please specify the path to an input file')
        sys.exit(2)
    
    if output_file == '':
        print('Please specify the path to an output file')
        sys.exit(2)
        
    excel_file = pandas.read_excel(input_file, header=None)
    metrics = (list(excel_file[0]))
    bottom = index_contains(metrics, 'bottom') + 1
    baseline = index_contains(metrics, 'baseline')
    pixels_below_baseline = bottom - baseline
    y_size = bottom - index_contains(metrics, 'top')

    font = NewFont(familyName=font_name, showInterface=False)
    font.info.unitsPerEm = 1000

    def getMeasurement(measurement):
        position = index_contains(metrics, measurement)
        return (bottom - pixels_below_baseline - position) * pixel_size

    try:
        layer = font.layers[0]
        layer.name = 'Regular'

        pixel_size = int(font.info.unitsPerEm / y_size)
        font.info.xHeight = getMeasurement("xheight") 
        font.info.capHeight = getMeasurement("capheight") 
        font.info.ascender = getMeasurement("ascender") 
        font.info.descender = getMeasurement("descender") 

        current_row = 0

        glyphs = {}

        # iterate over each row of lettering in Excel
        # ... and grab the glyph names and locations of the data
        while current_row < len(excel_file.index):
            glyph_positions = excel_file[current_row:current_row + 1].values.tolist()[0][1:]
            glyph_data = excel_file[current_row + 1:current_row + y_size + 1].values.tolist()
            glyph_names = set([item for item in glyph_positions if isinstance(item, str)])

            for glyph in glyph_names:
                glyphs[glyph] = []
                start_position = glyph_positions.index(glyph)
                end_position = next(i for i in reversed(range(len(glyph_positions))) if glyph_positions[i] == glyph)

                for row in glyph_data:
                    glyphs[glyph].append(row[start_position + 1:end_position + 2])

            current_row += (y_size + 1)

        for glyph_name, glyph_pixels in glyphs.items():
            glyph = font.newGlyph(glyph_name)
            
            glyph.unicode = ord(agl.toUnicode(glyph_name))
            glyph.width = (len(glyph_pixels[0]) * pixel_size)

            for row_number, row_data in enumerate(glyph_pixels):
                row_position = y_size - row_number - pixels_below_baseline - 1
                for col_number, col_data in enumerate(row_data):
                    if str(col_data) == '1':
                        rect = draw_pixel( row_position, col_number, pixel_size )
                        glyph.appendContour(rect)
            glyph.removeOverlap()

        if font_format == 'ufo':
            font.save(output_file)
        else:
            font.save('./tmp/tmpFont.ufo')
            fontmaker = font_project.FontProject()
            ufo = fontmaker.open_ufo('./tmp/tmpFont.ufo')
            if font_format == 'otf':
                fontmaker.build_otfs([ufo], output_path=output_file)
            else:
                fontmaker.build_ttfs([ufo], output_path=output_file)
            rmtree('./tmp/tmpFont.ufo')

        print('Job done. Enjoy the pixels.')
    except Exception as e:
        print('Script error!')
        raise e

if __name__ == "__main__":
   main(sys.argv[1:])
