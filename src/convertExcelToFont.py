#!/usr/bin/python3

import json
import sys
import getopt
from shutil import rmtree
from metrics import getHeight, getDepth
from drawing import drawPixel
from style import getHumanReadableStyle, expandStyle, expandFlags
from utils import chunks, getRange, getNiceGlyphName
from fontParts.world import *
from fontmake import font_project
import pandas


def main(argv):
    inputFile = ''
    outputFile = ''
    fontFormat = ''
    fontName = ''
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
            inputFile = arg
        elif opt in ("-o", "--output_file"):
            outputFile = arg
        elif opt in ("-f", "--format"):
            fontFormat = arg
            if fontFormat not in ('ufo', 'ttf', 'otf'):
                print('Format must be one of ufo, ttf, otf')
                sys.exit(2)
        elif opt in ("-n", "--name"):
            fontName = arg

    if inputFile == '':
        print('Please specify the path to an input file')
        sys.exit(2)
    
    if outputFile == '':
        print('Please specify the path to an output file')
        sys.exit(2)
        

    excelFile = pandas.read_excel(inputFile, header=None)
    print(excelFile)
    metrics = (list(excelFile[0]))
    print(metrics)
    ySize = metrics.index('bottom') - metrics.index('top')
    ascender = metrics.index('bottom') - metrics.index('ascender')
    capHeight = metrics.index('bottom') - metrics.index('capHeight')
    baseline = metrics.index('bottom') - metrics.index('baseline')
    xHeight = metrics.index('bottom') - metrics.index('xheight')
    descender = metrics.index('bottom') - metrics.index('descender')


    fontBitmapRows = list(chunks(fontBitArray, modulo * 8))

    print('Parsing', fontName)
    print(flagsDict, styleDict)

    glyphs = {}

    for i in range(0, charRange):
        charCode = loChar + i
        locationStart = int.from_bytes(locationData[i * 4:i * 4 + 2], byteorder='big', signed=False)
        bitLength = int.from_bytes(locationData[i * 4 + 2:i * 4 + 4], byteorder='big', signed=False)
        charCodeIndex = '.notdef' if charCode > hiChar else str(charCode)
        glyphs[charCodeIndex] = {
            "character": '.notdef' if charCode > hiChar else chr(charCode),
            "bitmap": list(map(lambda arr: getRange(arr, locationStart, bitLength), fontBitmapRows))
        }
        if flagsDict['proportional']:
            glyphs[charCodeIndex]['kerning'] = int.from_bytes(kerningData[i * 2: i * 2 + 2], byteorder='big', signed=True)
            glyphs[charCodeIndex]['spacing'] = int.from_bytes(spacingData[i * 2: i * 2 + 2], byteorder='big', signed=True)

    font = NewFont(familyName=fontName, showInterface=False)
    font.info.unitsPerEm = 1000


    try:
        layer = font.layers[0]
        layer.name = getHumanReadableStyle(styleDict)

        pixelSize = int(font.info.unitsPerEm / ySize)
        print('Font size:', ySize, '... Baseline:', baseline, '...Block size:', pixelSize)
        pixelsBelowBaseline = ySize - baseline
        font.info.xHeight = xHeight * pixelSize
        font.info.capHeight = capHeight * pixelSize        # work out ascender from the letter b (ASCII code 98)
        font.info.ascender = ascender * pixelSize
        font.info.descender = descender * pixelSize



        for char, amigaGlyph in glyphs.items():
            if amigaGlyph['character'] == '.notdef':
                glyphName = '.notdef'
            else:
                unicodeInt = ord(amigaGlyph['character'])
                glyphName = getNiceGlyphName(unicodeInt)
                print('Creating', unicodeInt, glyphName)

            glyph = font.newGlyph(glyphName)
            
            if amigaGlyph['character'] != '.notdef':
                glyph.unicode = unicodeInt

            glyph.width = ((amigaGlyph['spacing'] + amigaGlyph['kerning']) * pixelSize) if flagsDict['proportional'] else (xSize * pixelSize)

            for rowNumber, rowData in enumerate(amigaGlyph['bitmap']):
                rowPosition = ySize - rowNumber - pixelsBelowBaseline
                for colNumber, colData in enumerate(rowData):
                    colPosition = (colNumber + amigaGlyph['kerning']) if flagsDict['proportional'] else colNumber
                    if colData == '1':
                        rect = drawPixel( rowPosition, colPosition, pixelSize )
                        glyph.appendContour(rect)
            glyph.removeOverlap()

        if fontFormat == 'ufo':
            font.save(outputFile)
        else:
            font.save('./tmp/tmpFont.ufo')
            fontmaker = font_project.FontProject()
            ufo = fontmaker.open_ufo('./tmp/tmpFont.ufo')
            if fontFormat == 'otf':
                fontmaker.build_otfs([ufo], output_path=outputFile)
            else:
                fontmaker.build_ttfs([ufo], output_path=outputFile)
            rmtree('./tmp/tmpFont.ufo')

        print('Job done. Enjoy the pixels.')
    except Exception as e:
        print('Script error!')
        raise e

if __name__ == "__main__":
   main(sys.argv[1:])
