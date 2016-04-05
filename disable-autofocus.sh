#! /bin/sh

#
# Configure the stereo USB cameras
#

# Disable autofocus
uvcdynctrl -v -d video0 --set='Focus, Auto' 0
uvcdynctrl -v -d video1 --set='Focus, Auto' 0

# Fix the focus
uvcdynctrl -v -d video0 --set='Focus (absolute)' 30
uvcdynctrl -v -d video1 --set='Focus (absolute)' 30

# Fix power line frequency
uvcdynctrl -v -d video0 --set='Power Line Frequency' 1
uvcdynctrl -v -d video1 --set='Power Line Frequency' 1
