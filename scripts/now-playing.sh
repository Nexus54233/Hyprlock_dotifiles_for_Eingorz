#!/bin/bash
# Save this as ~/.config/hypr/scripts/now-playing.sh
# Make it executable: chmod +x ~/.config/hypr/scripts/now-playing.sh

# Get the currently playing track info
artist=$(playerctl metadata artist 2>/dev/null)
title=$(playerctl metadata title 2>/dev/null)

if [ -z "$artist" ] || [ -z "$title" ]; then
    echo "No music playing"
else
    echo "♪ $title - $artist"
fi


