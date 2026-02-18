#!/bin/bash
# Launch Khemist Lab Dashboard

echo "🧪 Starting Khemist Lab..."
echo "=========================="
echo ""
echo "Opening dashboard in your default browser..."
echo ""

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Open the HTML file
open "$DIR/lab-dashboard/index.html"

echo "✅ Lab Dashboard launched!"
echo ""
echo "Features:"
echo "  • Drag & drop task management"
echo "  • Real-time clock"
echo "  • Animated particle background"
echo "  • Trading stats integration"
echo ""
echo "Press Ctrl+C to stop watching (browser stays open)"
echo ""

# Optional: Watch for changes and auto-refresh (if fswatch is installed)
if command -v fswatch &> /dev/null; then
    echo "Watching for changes..."
    fswatch -o "$DIR/lab-dashboard" | while read; do
        echo "Files changed - refresh browser to see updates"
    done
else
    echo "Install fswatch for auto-refresh: brew install fswatch"
    echo "Dashboard is running. Refresh browser manually to see updates."
fi
