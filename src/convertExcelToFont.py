#!/usr/bin/python3
import sys
import getopt
from shutil import rmtree
from drawing import drawPixel
from utils import index_contains
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
    metrics = (list(excelFile[0]))
    bottom = index_contains(metrics, 'bottom')
    ySize = bottom - index_contains(metrics, 'top') + 1
    ascender = bottom - index_contains(metrics, 'ascender')
    capHeight = bottom - index_contains(metrics, 'capheight')
    xHeight = bottom - index_contains(metrics, 'xheight')
    baseline = bottom - index_contains(metrics, 'baseline')
    descender = bottom - index_contains(metrics, 'descender')

    font = NewFont(familyName=fontName, showInterface=False)
    font.info.unitsPerEm = 1000

    try:
        layer = font.layers[0]
        layer.name = 'Regular'

        pixelSize = int(font.info.unitsPerEm / ySize)
        print('Font size:', ySize, '... Baseline:', baseline, '...Block size:', pixelSize)
        pixelsBelowBaseline = ySize - baseline
        font.info.xHeight = (xHeight - pixelsBelowBaseline) * pixelSize 
        font.info.capHeight = (capHeight - pixelsBelowBaseline) * pixelSize        # work out ascender from the letter b (ASCII code 98)
        font.info.ascender = (ascender - pixelsBelowBaseline) * pixelSize
        font.info.descender = (descender - pixelsBelowBaseline) * pixelSize

        currentRow = 0

        glyphs = {}

        while currentRow < len(excelFile.index):
            glyphPositions = excelFile[currentRow:currentRow + 1].values.tolist()[0][1:]
            glyphData = excelFile[currentRow + 1:currentRow + ySize + 1].values.tolist()
            print(glyphPositions, glyphData)

            glyphNames = set([item for item in glyphPositions if isinstance(item, str)])
            for glyph in glyphNames:
                glyphs[glyph] = []
                startPos = glyphPositions.index(glyph)
                endPos = next(i for i in reversed(range(len(glyphPositions))) if glyphPositions[i] == glyph)
                print(glyph, startPos, endPos)

                for row in glyphData:
                    glyphs[glyph].append(row[startPos + 1:endPos + 2])

            currentRow += (ySize + 1)

            print(glyphs['B'])

        for glyphName, glyphPixels in glyphs.items():
            print('Creating', glyphName)

            glyph = font.newGlyph(glyphName)

            glyph.width = (len(glyphPixels[0]) * pixelSize)

            for rowNumber, rowData in enumerate(glyphPixels):
                rowPosition = ySize - rowNumber - pixelsBelowBaseline
                for colNumber, colData in enumerate(rowData):
                    colPosition = colNumber
                    if str(colData) == '1':
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
