# InsightCapture
Advanced Windows activity monitoring tool with screenshot capture, active window tracking, smart storage management, and keyword-based screenshot preservation.
# InsightCapture

InsightCapture is a Python-based desktop activity monitoring and logging utility designed for educational, research, productivity tracking, and digital forensics environments.

The application records active window activity, captures periodic screenshots, maintains a screenshot storage pool, and intelligently preserves screenshots containing important keywords related to authentication or transaction workflows.

## Features

- Active window title monitoring
- Continuous keyboard activity logging
- Automated screenshot capture
- Configurable screenshot intervals
- Smart screenshot retention system
- Keyword-based screenshot preservation
- Automatic cleanup of non-important screenshots
- Session start and end time logging

## Technologies Used

- Python
- PyAutoGUI
- Pynput
- Win32GUI
- PIL (Pillow)
- Pytesseract (optional OCR analysis)

## How It Works

1. Monitors the currently active application window.
2. Records keyboard activity into a log file.
3. Captures screenshots at configured intervals.
4. Analyzes screenshots and window titles for predefined keywords.
5. Preserves potentially important screenshots.
6. Removes older screenshots when storage limits are exceeded.
7. Generates activity logs for review and analysis.

## Configuration

Key settings can be modified directly within the source code:

- Screenshot Interval
- Maximum Screenshot Pool Size
- Output Directory
- Activity Log Location
- Keyword Preservation List

## Project Structure
