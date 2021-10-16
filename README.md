# Minecraft 3d Printing

This program can read gcode 3d print files and 'print' the model as blocks in Minecraft.

To use it, just choose your 3d model, prepare it in a program for printing such as Cura or Slic3r and then run this program.

# Install
To install this program, you'll need [python 3](https://www.python.org/downloads/). Install the latest version.
Then run the following command in this project folder:
`pip install pywinauto`

This is the only library needed.

# Running the Script
Run the script:
`python .\mc3d.py [any-print.gcode]`

It is expecting the second parameter to be the relative path to the .gcode file you want to print.

When it starts to run, quickly switch to Minecraft and open the command window (by typing `/` but then clearing it).

Then this script will type the `/setblock` commands to 'print' the 3d model.


