# VCore External Bot: Live Screen Capture, Vision, and Automation

This project is built as a legitimate external automation prototype for a carrom game. It intentionally does not modify the game code or inject into game internals. Instead, it uses a real-time screen capture + computer vision + automation loop.

## High-level workflow

1. Capture the live game screen from emulator/device.
2. Detect the board, pockets, striker, and coins from the image.
3. Compute the best shot using VCore shot ranking and trajectory prediction.
4. Convert the selected shot into touch coordinates.
5. Send synthetic input to the emulator/device.
6. Observe the result and repeat the loop.

## Core modules

- `vcore.capture.screen_capture` — ADB screenshot capture
- `vcore.control.input_controller` — swipe/tap automation
- `vcore.vision.board_detector_cv` — board, coin, and pocket detection
- `vcore.physics` — shot simulation and candidate ranking
- `examples/live_bot_demo.py` — end-to-end demo for external bot logic

## Important limitations

This is not a guaranteed hack or cheat against a proprietary game. Real-world success depends on:

- device/emulator visibility and screen scaling
- stable frame detection
- board calibration and coin detection accuracy
- the game’s actual UI and touch interaction model
- device automation support and anti-cheat behavior

## Setup

Install Python dependencies:

```bash
python -m pip install opencv-python numpy pillow scipy adb-shell
```

Ensure ADB is available and your emulator/device is connected:

```bash
adb devices
```

## Run the demo

```bash
python -m examples.live_bot_demo
```

## Notes

This architecture is designed as a modular, testable prototype. It is intentionally separated from the internal game engine and can be adapted to different devices or emulators.
