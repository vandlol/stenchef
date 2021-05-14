#!/usr/bin/env python3

from reportlab.lib.utils import simpleSplit
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
import argparse
import re


# font metrics
def getTextHeight(fontName, fontSize):
    face = pdfmetrics.getFont(fontName).face
    ascent = (face.ascent * fontSize) / 1000.0
    descent = (face.descent * fontSize) / 1000.0
    height = ascent - descent  # <-- descent it's negative
    return height


def split_text(text, delim):
    mid = min(
        (i for i, c in enumerate(text) if c == delim),
        key=lambda i: abs(i - len(text) // 2),
    )
    return (text[:mid], "{}{}".format(delim, text[mid + 1 :]))


"""parser = argparse.ArgumentParser(
    "Print labels for dymo label writer, optionally with a qr code and an icon"
)
parser.add_argument("--text", type=str, help="Text")
parser.add_argument("--font_size", type=int, default=10)
parser.add_argument("--font", type=str, default="Helvetica")
args = parser.parse_args()
if args.text:
    text = args.text"""

def format_label(text):
    pdfmetrics.registerFont(TTFont("Arial", "Arial.ttf"))
    label_dims = (2.244 * inch, 1.259 * inch)
    item_spacing = 4
    leftMargin = 4
    default_font_size = 14
    default_font = "Arial"
    perc_free = 5
    minimum_font_size = 9

    #if not args.font_size:
    current_font_size = default_font_size
    #else:
    #    current_font_size = args.font_size

    #if not args.font:
    current_font = default_font
    #else:
    #    current_font = args.font

    # create label
    c = canvas.Canvas("label.pdf", pagesize=label_dims)
    c.setFont(current_font, current_font_size)
    c.translate(leftMargin, 0)

    maxWidth = label_dims[0] - leftMargin - item_spacing - (label_dims[0] / 100 * perc_free)

    lineHeight = getTextHeight(current_font, current_font_size)
    lines = text.split("\n")
    if len(lines) < 3:
        lines = text.split("\\n")


    size = 1
    while size == 1:
        broken = 0
        for i in range(len(lines)):
            if current_font_size <= minimum_font_size:
                if (
                    len(simpleSplit(lines[i], current_font, current_font_size, maxWidth))
                    > 1
                ):
                    current_font_size += 2
                    c.setFont(current_font, current_font_size)
                    if re.match(
                        r"^\d+$",
                        simpleSplit(lines[i], current_font, current_font_size, maxWidth)[
                            -1
                        ],
                    ):
                        part1, part2 = split_text(lines[i], "-")
                    else:
                        part1, part2 = split_text(lines[i], " ")
                    lines[i] = part1
                    lines.insert(i + 1, part2)
                    size = 0
                    break
                continue
            if len(simpleSplit(lines[i], current_font, current_font_size, maxWidth)) > 1:
                current_font_size -= 1
                c.setFont(current_font, current_font_size)
                broken = 1
                break
        if broken == 0:
            size = 0

    totalHeight = len(lines) * lineHeight
    c.translate(0, (label_dims[1] - totalHeight) / 2 + totalHeight - lineHeight)

    # print each line
    for i in range(len(lines)):
        c.drawString(0, -lineHeight * i, lines[i])

    c.save()

"""if __name__ == "__main__":
    format_label() """