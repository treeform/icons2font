icons2font
==========

This utility takes vector icons in svg format and convert them to icon fonts (svg,ttf,waff,eot) to be display in all browsers.

Usage
=====


	icons2font.py [-h] [--baseline BASELINE] name src [dest]

	This utility takes vector icons in svg format and converts them to icon fonts
	(svg,ttf,waff,eot) to be display in all browsers. requires python-fontforge

	positional arguments:
	  name                 name of the icon font you want
	  src                  folder wher the svg glyphs are
	  dest                 folder to output the stuff

	optional arguments:
	  -h, --help           show this help message and exit
	  --baseline BASELINE  adjust generated chars up or down

example
-------
    python icons2font.py my_awesome_font ~/some_svgs ~/i2f_output --baseline 2
