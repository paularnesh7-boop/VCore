#!/usr/bin/env python3
"""
Usage Guide: Running the VCore External Bot

This guide walks through the complete setup and execution.
"""

# ============================================================================
# SETUP: Prerequisites
# ============================================================================

"""
1. Install Python 3.10+
   Download from: https://www.python.org/downloads/

2. Install required packages:
   pip install opencv-python numpy pillow scipy adb-shell

3. Install ADB (Android Debug Bridge)
   - Windows: Download Android SDK Platform Tools from Google
   - macOS: brew install android-platform-tools
   - Linux: sudo apt-get install adb

4. Setup Android Emulator
   - Download Bluestacks, NoxPlayer, or Android Studio Emulator
   - Launch emulator
   - Ensure "USB Debugging" is enabled

5. Verify ADB Connection
   adb devices
   # Should show: emulator-5554    device
"""

# ============================================================================
# QUICK START
# ============================================================================

"""
Step 1: Clone/Setup VCore Repository

  cd /path/to/VCore
  pip install -e .

Step 2: Connect Android Emulator

  # In emulator terminal or system:
  adb devices
  # Verify device appears in list

Step 3: Run Board Detection Debug (Recommended First)

  python -m vcore.vision.board_detector_debug
  
  This will:
  - Capture a screenshot
  - Show step-by-step detection process
  - Save debug images to: board_detection_debug/
  - Let you verify accuracy

Step 4: Run Full Bot Loop

  python -m vcore.bot.full_bot_loop
  
  This will:
  - Calibrate the board
  - Take up to 10 shots
  - Save screenshots to: vcore_output/
  - Print detailed logs
"""

# ============================================================================
# DETAILED WORKFLOW
# ============================================================================

"""
### Phase 1: Board Calibration

The bot needs to learn the mapping between board game coordinates and screen pixel coordinates.

Process:
1. Capture frame from emulator
2. Detect board corners in the image
3. Create a perspective transform matrix
4. All future coordinates are mapped through this matrix

Example output:
  Board corners detected: (54, 48), (1026, 48), (54, 1920), (1026, 1920)
  Calibration set. Board: 972x1872, Screen corners: ...

### Phase 2: Board State Detection

For each frame, detect:
- Coin positions (black, red, white/striker)
- Pocket positions (6 holes at board edges)
- Striker position (large white coin)

Output includes all coin coordinates and colors.

### Phase 3: Shot Planning

For detected board state:
1. Generate candidate shots from each coin to each pocket
2. Score each shot by distance and expected value
3. Simulate trajectory using physics engine
4. Select top-ranked shot

Example:
  Shot 1: Attempt to pocket coin c1 into pocket 0.
  angle=42.5°, force=0.73

### Phase 4: Shot Execution

Convert board coordinates to screen coordinates:
1. Map striker position from board to screen
2. Calculate aim angle and force from physics
3. Send ADB swipe/tap commands
4. Wait for animation

Example:
  Swipe: (350, 960) → (420, 1050) in 0.3s
  Waiting 2.5s for animation to complete...

### Phase 5: Outcome Observation

After animation:
1. Capture new frame
2. Detect board state again
3. Compare before/after
4. Count newly pocketed coins
5. Log success/miss

Example:
  Outcome: success, Coins pocketed: 1, Total: 3
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
### Issue: "No ADB devices found"

Solution:
- Ensure emulator is running
- Run: adb devices
- If not listed, restart emulator
- Check: adb kill-server && adb start-server

### Issue: "Board corners not detected"

Solution:
- Run debug detector: python -m vcore.vision.board_detector_debug
- Check output images in board_detection_debug/
- Verify board is clearly visible in game
- Adjust Canny edge detection thresholds if needed

### Issue: "Coins not detected"

Solution:
- Check HSV color ranges for your game version
- Run debug detector and inspect 04_coins_*.png
- Adjust minRadius/maxRadius in HoughCircles
- Ensure lighting is consistent

### Issue: "Shots are inaccurate"

Solution:
- Run board_detector_debug and verify 02_game_region.png
- Check calibration output: verify corner coordinates
- Test with manual game play first
- Increase shot_delay in bot loop if animation isn't done

### Issue: "Touch input not working"

Solution:
- Verify device ID: adb devices
- Test basic tap: adb shell input tap 500 500
- Check emulator input settings
- Try different emulator (Bluestacks vs NoxPlayer)
"""

# ============================================================================
# CONFIGURATION & TUNING
# ============================================================================

"""
Edit vcore/bot/full_bot_loop.py to tune:

1. SCREEN CAPTURE
   - capture_screenshot() timeout
   - Device ID selection

2. BOARD DETECTION
   - Canny thresholds (50, 150)
   - HoughCircles parameters (minRadius, maxRadius)
   - HSV color ranges for coins

3. PHYSICS
   - Friction coefficient
   - Restitution
   - Coin/pocket radius

4. INPUT EXECUTION
   - Swipe duration
   - Tap delay
   - Force scaling

5. TIMING
   - shot_delay: How long to wait for animation (default: 2.5s)
   - capture delay: Time between frames

Example modifications:

# Increase animation wait time
bot.run_full_loop(max_shots=5, shot_delay=3.5)

# Enable debug output
bot = VCoreLiveBot(debug=True)

# Reduce number of shots for testing
bot.run_full_loop(max_shots=2)
"""

# ============================================================================
# PERFORMANCE & ACCURACY
# ============================================================================

"""
Expected Performance:

- Screen capture FPS: 1-2 fps (limited by ADB)
- Detection accuracy: 85-95% (depends on board state)
- Shot planning time: <100ms
- Input execution: 1-2 seconds per shot
- Total cycle time: 4-7 seconds per shot

Accuracy Factors:
1. Board detection quality (biggest impact)
2. Coin overlap (decreases accuracy)
3. Physics simulation accuracy
4. Touch input calibration
5. Game animation timing

Tips for Better Accuracy:
1. Use high-resolution emulator (1080p+)
2. Ensure consistent lighting
3. Run calibration before each session
4. Add manual calibration points if corners unclear
5. Increase detection thresholds if noisy
"""

# ============================================================================
# DEBUG OUTPUT
# ============================================================================

"""
The bot saves debug images and logs:

Debug Images (board_detection_debug/):
  01_original.png           - Raw screenshot
  02_game_region.png        - Cropped board area
  03_grayscale.png          - Grayscale conversion
  04_edges.png              - Canny edge detection
  05_final_detection.png    - All detections overlaid

Bot Output (vcore_output/):
  00_before_shot.png        - Board before shot 1
  00_after_shot.png         - Board after shot 1
  01_before_shot.png        - Board before shot 2
  ... etc

Logs:
  Console output with timestamps
  Success/miss outcomes
  Coordinate mappings
  Error messages
"""

# ============================================================================
# NEXT STEPS
# ============================================================================

"""
1. Run board detection debug
2. Verify detection accuracy
3. Adjust parameters if needed
4. Run full bot loop
5. Monitor accuracy
6. Iterate on detection/physics

Advanced enhancements:
- Add multi-shot planning (lookahead)
- Machine learning for parameter tuning
- Live calibration refinement
- Anti-cheat evasion (random delays)
- Performance optimization
"""
