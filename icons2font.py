import sys
import os
from xml.dom import minidom

GSIZE = 1400

HEADER = """<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd" >
<svg xmlns="http://www.w3.org/2000/svg">
<metadata></metadata>
<defs>
<font id="%s">
<font-face units-per-em="2048" ascent="1536" descent="-512" />
<missing-glyph horiz-adv-x="512" />
<glyph horiz-adv-x="0" />
<glyph horiz-adv-x="0" />
"""

GLYPH = """<glyph unicode="%s" horiz-adv-x="1400" d="%s" />\n\n"""

FOOTER = """

</font>
</defs>
</svg>
"""

DOC_HEADER = """
<!DOCTYPE html>
<!--[if lt IE 7 ]><html class="ie ie6" lang="en"> <![endif]-->
<!--[if IE 7 ]><html class="ie ie7" lang="en"> <![endif]-->
<!--[if IE 8 ]><html class="ie ie8" lang="en"> <![endif]-->
<!--[if (gte IE 9)|!(IE)]><!--><html lang="en"> <!--<![endif]-->
<head>
    <meta charset="utf-8" />
    <link rel="stylesheet" href="{0}.css">
    <style type="text/css">
        body {{
           font-size: 2em;
           color: black;
        }}
    </style
</head>
<body>
<h1>Font: {0}</h1>

"""
DOC_FOOTER = """
</body>
</html>
"""

#  src: url('{0}.eot');
#  src: url('{0}.eot') format('embedded-opentype'),
#       url('{0}.ttf') format('truetype'),
#       url('{0}.woff') format('woff'),
#       url('{0}.svg') format('svg');

CSS_HEADER = """
@font-face {{
  font-family: "{0}";
  src: url('{0}.svg') format('svg');
  font-weight: normal;
  font-style: normal;
}}


[class^="icon-"]:before, [class*=" icon-"]:before {{
  font-family: {0};
  font-weight: normal;
  font-style: normal;
  display: inline-block;
  text-decoration: inherit;
}}
"""


COMMANDS_ABS = "MZLHVCSQTA"
COMMANDS_REL = COMMANDS_ABS.lower()
COMMANDS = COMMANDS_ABS + COMMANDS_REL

def between(a, b, s):
    first = s.find(a)
    first += len(a)
    last = s.find(b, first)
    return s[first:last]

def htmlhex(n):
    return hex(n).replace("0x","&#x") + ";"

def svg_paths(svg):
    xmldoc = minidom.parseString(svg)
    paths = []

    # view box
    for s in xmldoc.getElementsByTagName('svg'):
        try:
            viewBox = map(float, s.attributes['viewBox'].value.split())
        except:

            viewBox = [0,0,
                float(s.attributes['width'].value),
                float(s.attributes['height'].value)]
    #    width="100" height="100"

    for s in xmldoc.getElementsByTagName('path'):
        d = s.attributes['d'].value
        paths.append(d)


    for s in xmldoc.getElementsByTagName('polygon'):
        d = s.attributes['points'].value
        paths.append("M"+d)

    for s in xmldoc.getElementsByTagName('rect'):
        try: x = float(s.attributes['x'].value)
        except: x = 0
        try: y = float(s.attributes['y'].value)
        except: y = 0

        w = float(s.attributes['width'].value)
        h = float(s.attributes['height'].value)
        p = ["M",x,y, x+w,y, x+w,y+h, x,y+h, x,y, "Z"]
        paths.append(" ".join(map(str,p)))

    for s in xmldoc.getElementsByTagName('circle'):
        cx = float(s.attributes['cx'].value)
        cy = float(s.attributes['cy'].value)
        r = float(s.attributes['r'].value)
        p =["M", cx-r, cy,
            "a", r,r,  0,  1,0,  (r*2),0,
            "a", r,r,  0,  1,0,  -(r*2),0,
            "Z"]
        paths.append(" ".join(map(str,p)))

        x = cx-r
        y = cy-r
        w = 2*r
        h = 2*r

        p = ["M",x,y, x+w,y, x+w,y+h, x,y+h, x,y, "Z"]
        #paths.append(" ".join(map(str,p)))


    return viewBox, paths

def parse_path(path):
    commands = []
    command = []
    word = []
    for c in path:
        if c in COMMANDS:
            if word:
                command.append(float("".join(word)))
                word = []
            if command:
                commands.append(command)
            command = [c]
        elif c in " ,":
            if word:
                command.append(float("".join(word)))
                word = []
        elif c in "+-":
            if word:
                command.append(float("".join(word)))
                word = []
            word.append(c)
        else:
            word.append(c)
    if word:
        command.append(float("".join(word)))
        word = []
    if command:
        commands.append(command)
    return commands

def compile_path(commands):
    buf = []
    for command in commands:
        buf.append(command[0])
        for n in command[1:]:
            buf.append(str(n))
    return " ".join(buf)

def compute_minrec():
    minx, miny, maxx, maxy = None, None, None, None
    pen = [0,0]
    rec = [None, None, None, None]
    def min_rec():
        # min rec calculate
        if rec[0] is None or rec[0] > pen[0]: rec[0] = pen[0]
        if rec[1] is None or rec[1] > pen[1]: rec[1] = pen[1]
        if rec[2] is None or rec[2] < pen[0]: rec[2] = pen[0]
        if rec[3] is None or rec[3] < pen[1]: rec[3] = pen[1]

    for command in commands:
        op = command[0]
        print command
        if op in "VvHhAa":
            # account for the stupid direction commands
            for n in command[1:]:
                if op == "V":
                    pen[0] = n
                elif op == "v":
                    pen[0] += n
                if op == "H":
                    pen[1] = n
                elif op == "h":
                    pen[1] += n
                if op == "A":
                    # arc command is insane
                    pass
                elif op == "a":
                    # arc command is insane
                    pass

                min_rec()
        else:
            # all other commands
            for p in range((len(command)-1)/2):
                x = command[1+p*2]
                y = command[2+p*2]
                # move the pen
                if op in COMMANDS_REL:
                    pen[0] += x
                    pen[1] += y
                else:
                    pen[0] = x
                    pen[1] = y

                min_rec()
    print "min rectangle", rec
    minx, miny, maxx, maxy = rec
    tranx = -minx
    trany = -miny
    sizex = maxx - minx
    sizey = maxy - miny


def do_glyph(f, glyphname, index, name, svg, doc, css):


    doc.write("<i class='"+glyphname+"'></i> "+glyphname+"<br/>\n")
    css.write('.{0}::before {{\n    content: "\{1}";\n}}\n'.format(glyphname, hex(index)[2:].lower()))

    data = open(name+"/"+f).read()

    print f

    viewBox, paths = svg_paths(data)
    # font needs to be of one path
    path = " ".join(paths)
    commands = parse_path(path)

    tranx, trany, sizex, sizey = viewBox
    tranx = -tranx
    trany = -trany

    size = max(sizex, sizey)
    scale = GSIZE/size

    if size - sizey > 0:
        trany += (size - sizey)/2
    if size - sizex > 0:
        tranx += (size - sizex)/2

    #print "translate", tranx, trany, "scale", scale

    prev_op = None
    for command in commands:
        op = command[0]

        if op in "Aa":
            # arcs require special fancy scaling
            command[1] *= scale
            command[2] *= scale
            # presurve flags
            command[4] = int(command[4])
            command[5] = int(command[5])
            # scale the radii
            command[6] *= scale
            command[7] *= scale
        else:
            for i,num in enumerate(command):
                if num == op: continue
                if op in COMMANDS_ABS:
                    if op == "H":
                        command[i] *= scale
                        command[i] += tranx * scale
                    elif op == "V":
                        command[i] *= -scale
                        command[i] += -trany * scale + GSIZE
                    else:
                        if i % 2 == 1:
                            command[i] *= scale
                            command[i] += tranx * scale
                        else:
                            command[i] *= -scale
                            command[i] += -trany * scale + GSIZE
                else:
                    if op in "h":
                        command[i] *= scale
                    elif op in "v":
                        command[i] *= -scale
                    else:
                        if i % 2 == 1:
                            command[i] *= scale
                        else:
                            command[i] *= -scale
        # special case for first relative m (its just like abs M)
        if op == "m" and prev_op == None:
            command[1] += tranx * scale
            command[2] += -trany * scale + GSIZE
        prev_op = op

    #commands.insert(0, ['M', tranx*scale, -trany*scale])

    path = compile_path(commands)
    #print "final path", path
    svg.write(GLYPH % (htmlhex(index), path))

def main():
    name = sys.argv[1]

    svg = open(name+".svg",'w')
    doc = open(name+".html",'w')
    css = open(name+".css",'w')

    svg.write(HEADER.format(name))
    doc.write(DOC_HEADER.format(name))
    css.write(CSS_HEADER.format(name))

    # use the special user area
    index = 0xf000

    for f in sorted(os.listdir(name)):
        glyphname = "icon-"+f.replace(".svg","").replace("_","-").replace(" ","-").lower()
        do_glyph(f, glyphname, index, name, svg, doc, css)
        index += 1

    doc.write(DOC_FOOTER)
    doc.close()
    css.close()
    svg.write(FOOTER)
    svg.flush()
    svg.close()

    os.system("fontforge -lang=ff -c 'Open($1); Generate($2); Generate($3);' {0}.svg {0}.ttf {0}.woff".format(name))
    os.system("ttf2eot {0}.ttf > {0}.eot".format(name))


if __name__ == "__main__":
    main()

