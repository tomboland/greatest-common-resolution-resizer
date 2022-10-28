#!/usr/bin/env python3.10
from dataclasses import dataclass
from typing import NewType, List
from enum import Enum, auto
from sh import magick
import sys

example = """
B.png PNG 1896x1072 1896x1072+0+0 8-bit sRGB 576310B 0.000u 0:00.000
G.png PNG 1912x1072 1912x1072+0+0 8-bit sRGB 644667B 0.000u 0:00.000
IR.png PNG 1896x1064 1896x1064+0+0 8-bit sRGB 623871B 0.000u 0:00.000
L.png PNG 1904x1080 1904x1080+0+0 8-bit sRGB 653065B 0.000u 0:00.000
R.png PNG 1904x1064 1904x1064+0+0 8-bit sRGB 583540B 0.000u 0:00.000
"""
example2 = """
/home/tom/astrophotography/luna-24-03-2021-2/5/b.fit FITS 1920x1072 1920x1072+0+0 32-bit Grayscale Gray 8328960B 0.060u 0:00.056
/home/tom/astrophotography/luna-24-03-2021-2/5/g.fit FITS 1920x1072 1920x1072+0+0 32-bit Grayscale Gray 8328960B 0.050u 0:00.055
/home/tom/astrophotography/luna-24-03-2021-2/5/ir.fit FITS 1896x1064 1896x1064+0+0 32-bit Grayscale Gray 8167680B 0.060u 0:00.053
/home/tom/astrophotography/luna-24-03-2021-2/5/l.fit FITS 1920x1080 1920x1080+0+0 32-bit Grayscale Gray 8392320B 0.070u 0:00.070
/home/tom/astrophotography/luna-24-03-2021-2/5/r.fit FITS 1920x1072 1920x1072+0+0 32-bit Grayscale Gray 8328960B 0.070u 0:00.070
"""

ImgFileName = NewType('ImgFileName', str)
ImgFileFormat = NewType('ImgFileFormat', str)
ImgXRes = NewType('ImgXRes', int)
ImgYRes = NewType('ImgYRes', int)


class ImgFileFormat(Enum):
    PNG = auto()
    FITS = auto()


@dataclass
class ImgResolution:
    x: ImgXRes
    y: ImgYRes


@dataclass
class ImgIdent:
    filename: ImgFileName
    file_format: ImgFileFormat
    resolution: ImgResolution


def file_extension_from_format(file_format: ImgFileFormat) -> str:
    match file_format:
        case ImgFileFormat.PNG: return ".png"
        case ImgFileFormat.FITS: return ".fit"


def img_filename_from_str(s: str) -> ImgFileName:
    return ImgFileName(s)


def img_file_format_from_str(s: str) -> ImgFileFormat:
    match s:
        case 'PNG': return ImgFileFormat.PNG
        case 'FITS': return ImgFileFormat.FITS


def img_resolution_from_str(s: str) -> ImgResolution:
    (xs, ys) = s.split('x')
    return ImgResolution(ImgXRes(int(xs)), ImgYRes(int(ys)))


def img_ident_from_str(s: str) -> ImgIdent:
    (file_name, file_format, resolution) = s.rstrip().split()
    return ImgIdent(
        img_filename_from_str(file_name),
        img_file_format_from_str(file_format),
        img_resolution_from_str(resolution)
    )


def greatest_common_resolution_from_idents(idents: List[ImgIdent]) -> ImgResolution:
    max_x = max([i.resolution.x for i in idents])
    max_y = max([i.resolution.y for i in idents])
    return ImgResolution(max_x, max_y)


if __name__ == "__main__":
    files = sys.argv[1:]
    o = magick.identify('-format', '%M %m %G\n', files, _iter=True)
    idents = [img_ident_from_str(line) for line in o]
    common_resolution = greatest_common_resolution_from_idents(idents)
    output_extent = f'{common_resolution.x}x{common_resolution.y}'
    for ident in idents:
        output_filename = f'{ident.filename}_resized{file_extension_from_format(ident.file_format)}'
        print(output_filename)
        magick(ident.filename, '-background', 'black', '-extent', output_extent, output_filename)
