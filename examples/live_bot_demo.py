#!/usr/bin/env python3
"""Live external bot demo for VCore."""

import logging
import time

from vcore.capture.screen_capture import ScreenCapture, ScreenAnalyzer
from vcore.control.input_controller import GameInteraction

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def main():
    logger = logging.getLogger('vcore_demo')
    try:
        capture = ScreenCapture()
        analyzer = ScreenAnalyzer()
        interaction = GameInteraction(capture.device_id)

        logger.info("Starting live screen analysis loop...")

        for i in range(3):
            frame = capture.capture_screenshot()
            if frame is None:
                logger.warning("No frame captured, retrying...")
                time.sleep(1)
                continue

            board = analyzer.extract_board_state(frame)
            if board is not None:
                logger.info(f"Board detection: {len(board['coins'])} coins, {len(board['pockets'])} pockets")
                if board['striker']:
                    logger.info(f"Striker: {board['striker']}")

                # Example shot based on board state
                # In a production implementation, this would use VCore decision engine.
                interaction.execute_shot(aim_angle=0.0, force=0.7)
                interaction.wait_for_strike_complete(timeout=2.5)

            time.sleep(1)

        logger.info("Demo complete.")
    except Exception as exc:
        logger.error(f"Demo failed: {exc}")


if __name__ == '__main__':
    main()
