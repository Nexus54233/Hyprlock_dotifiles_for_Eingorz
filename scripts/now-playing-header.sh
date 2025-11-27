#!/bin/bash
# Save this as ~/.config/hypr/scripts/now-playing-header.sh
# Make it executable: chmod +x ~/.config/hypr/scripts/now-playing-header.sh

# Get the player status
status=$(playerctl status 2>/dev/null)

if [ "$status" = "Paused" ]; then
    echo "STOPPED"
else
    echo "NOW PLAYING"
fi

