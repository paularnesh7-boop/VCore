#!/usr/bin/env python3
"""
VCore Full External Bot Loop

Complete end-to-end automation:
1. Capture screen from device
2. Detect board, coins, pockets
3. Calculate best shot using VCore
4. Execute shot via ADB input
5. Observe result and repeat
"""

import logging
import time
import math
import numpy as np
import cv2
from typing import Optional, Tuple, List, Dict
from pathlib import Path

from vcore.capture.screen_capture import ScreenCapture, ScreenAnalyzer
from vcore.control.input_controller import GameInteraction
from vcore.physics import ShotAnalyzer, PhysicsEngine
from vcore.board import BoardState, Coin

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('VCore.FullBot')


class BoardCalibration:
    """
    Calibrates the mapping between screen coordinates and board coordinates.
    Stores the board corners and provides coordinate transformation functions.
    """

    def __init__(self):
        self.screen_corners = None  # Screen coordinates of board corners
        self.board_corners = None   # Board game coordinates
        self.board_width = 600.0
        self.board_height = 600.0
        self.calibrated = False
        logger.info("BoardCalibration initialized")

    def set_corners(self, screen_corners: Tuple, board_width: float = 600.0, board_height: float = 600.0):
        """
        Set board corners in screen space.
        screen_corners: (top-left, top-right, bottom-left, bottom-right)
        """
        self.screen_corners = screen_corners
        self.board_width = board_width
        self.board_height = board_height
        self.board_corners = [
            (0, 0),
            (board_width, 0),
            (0, board_height),
            (board_width, board_height)
        ]
        self.calibrated = True
        logger.info(f"Calibration set. Board: {board_width}x{board_height}, Screen corners: {screen_corners}")

    def board_to_screen(self, board_x: float, board_y: float) -> Tuple[int, int]:
        """
        Convert board coordinates to screen coordinates using perspective transform.
        """
        if not self.calibrated:
            logger.warning("Calibration not set, returning approximate screen coords")
            return (int(board_x), int(board_y))

        # Create perspective transform matrix
        board_pts = np.float32(self.board_corners)
        screen_pts = np.float32(self.screen_corners)
        matrix = cv2.getPerspectiveTransform(board_pts, screen_pts)

        # Transform point
        point = np.float32([[[board_x, board_y]]])
        transformed = cv2.perspectiveTransform(point, matrix)
        x, y = transformed[0][0]
        return (int(x), int(y))

    def screen_to_board(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """
        Convert screen coordinates to board coordinates.
        """
        if not self.calibrated:
            logger.warning("Calibration not set, returning approximate board coords")
            return (float(screen_x), float(screen_y))

        board_pts = np.float32(self.board_corners)
        screen_pts = np.float32(self.screen_corners)
        matrix = cv2.getPerspectiveTransform(screen_pts, board_pts)

        point = np.float32([[[screen_x, screen_y]]])
        transformed = cv2.perspectiveTransform(point, matrix)
        x, y = transformed[0][0]
        return (float(x), float(y))


class VCoreLiveBot:
    """
    Full external bot loop:
    1. Capture screen
    2. Detect board state
    3. Plan shot using VCore
    4. Execute via ADB
    5. Repeat
    """

    def __init__(self, device_id: Optional[str] = None, debug: bool = False):
        self.capture = ScreenCapture(device_id)
        self.analyzer = ScreenAnalyzer()
        self.interaction = GameInteraction(self.capture.device_id)
        self.calibration = BoardCalibration()
        self.debug = debug
        self.shot_count = 0
        self.pocketed_count = 0
        self.output_dir = Path("vcore_output")
        self.output_dir.mkdir(exist_ok=True)
        logger.info(f"VCoreLiveBot initialized (debug={debug})")

    def calibrate_board(self) -> bool:
        """
        Capture a frame and manually detect board corners for calibration.
        Returns True if calibration successful.
        """
        logger.info("Starting board calibration...")
        frame = self.capture.capture_screenshot()
        if frame is None:
            logger.error("Failed to capture screen for calibration")
            return False

        # Save raw frame
        if self.debug:
            cv2.imwrite(str(self.output_dir / "01_raw_frame.png"), frame)

        # Detect board corners
        corners = self.analyzer.detect_board_corners(frame)
        if corners is None:
            logger.error("Failed to detect board corners")
            return False

        logger.info(f"Board corners detected: {corners}")
        game_region = self.analyzer.get_game_region(frame)
        if game_region is not None:
            self.calibration.set_corners(
                corners,
                board_width=float(game_region.shape[1]),
                board_height=float(game_region.shape[0])
            )
            logger.info("Calibration successful")
            return True

        return False

    def detect_board_state(self, frame: np.ndarray) -> Optional[BoardState]:
        """
        Detect complete board state from a screen frame.
        Returns BoardState or None if detection fails.
        """
        try:
            board_data = self.analyzer.extract_board_state(frame)
            if not board_data:
                logger.warning("Failed to extract board state")
                return None

            # Convert to VCore BoardState
            coins = []
            striker = None

            for coin_data in board_data['coins']:
                coin = Coin(
                    id=coin_data['id'],
                    x=coin_data['x'],
                    y=coin_data['y'],
                    radius=coin_data['radius'],
                    color=coin_data['color'],
                    pocketed=False,
                    is_striker=coin_data.get('is_striker', False)
                )
                if coin.is_striker:
                    striker = coin
                else:
                    coins.append(coin)

            if striker is None:
                logger.warning("No striker detected, using default")
                striker = Coin(
                    id="striker",
                    x=board_data['width'] * 0.15,
                    y=board_data['height'] * 0.5,
                    radius=18.0,
                    color="white",
                    is_striker=True
                )

            board = BoardState(
                width=board_data['width'],
                height=board_data['height'],
                pockets=board_data['pockets'],
                striker=striker,
                coins=coins
            )
            logger.info(f"Board detected: {len(coins)} coins, {len(board.pockets)} pockets")
            return board

        except Exception as e:
            logger.error(f"Board state detection failed: {e}")
            return None

    def select_and_execute_shot(self, board: BoardState) -> bool:
        """
        Select best shot using VCore and execute via ADB.
        Returns True if shot was executed.
        """
        try:
            # Generate candidates and select best
            analyzer = ShotAnalyzer()
            candidates = analyzer.generate_shot_candidates(board)

            if not candidates:
                logger.warning("No valid shot candidates available")
                return False

            best_shot = candidates[0]
            logger.info(
                f"Shot {self.shot_count + 1}: {best_shot.description} "
                f"(angle={math.degrees(best_shot.angle):.1f}°, force={best_shot.force:.2f})"
            )

            # Calculate striker screen position for aiming
            striker_screen = self.calibration.board_to_screen(
                board.striker.x,
                board.striker.y
            )
            logger.debug(f"Striker screen position: {striker_screen}")

            # Set board center for input controller
            board_center_screen = self.calibration.board_to_screen(
                board.width / 2,
                board.height / 2
            )
            self.interaction.set_board_center(board_center_screen[0], board_center_screen[1])

            # Execute the shot
            self.interaction.execute_shot(best_shot.angle, best_shot.force)
            self.shot_count += 1

            # Save prediction for comparison
            predicted_state = PhysicsEngine.simulate_shot(
                board,
                best_shot.angle,
                best_shot.force
            )
            predicted_pocketed = sum(1 for c in predicted_state.coins if c.pocketed)
            logger.info(f"Predicted outcome: {predicted_pocketed} coins pocketed")

            return True

        except Exception as e:
            logger.error(f"Shot execution failed: {e}")
            return False

    def observe_and_compare(self, frame_before: np.ndarray, frame_after: np.ndarray) -> Dict:
        """
        Compare board state before and after shot.
        Returns outcome metrics.
        """
        try:
            board_before = self.detect_board_state(frame_before)
            board_after = self.detect_board_state(frame_after)

            if not board_before or not board_after:
                return {'status': 'detection_failed'}

            pocketed_before = sum(1 for c in board_before.coins if c.pocketed)
            pocketed_after = sum(1 for c in board_after.coins if c.pocketed)
            newly_pocketed = pocketed_after - pocketed_before

            self.pocketed_count += newly_pocketed

            outcome = {
                'status': 'success' if newly_pocketed > 0 else 'miss',
                'coins_pocketed': newly_pocketed,
                'total_pocketed': pocketed_after,
                'striker_moved': math.hypot(
                    board_after.striker.x - board_before.striker.x,
                    board_after.striker.y - board_before.striker.y
                )
            }

            logger.info(f"Outcome: {outcome['status']}, Coins pocketed: {newly_pocketed}, Total: {pocketed_after}")
            return outcome

        except Exception as e:
            logger.error(f"Outcome comparison failed: {e}")
            return {'status': 'comparison_failed'}

    def run_full_loop(self, max_shots: int = 10, shot_delay: float = 2.5):
        """
        Run the complete bot loop for a full game.
        
        Args:
            max_shots: Maximum number of shots to attempt
            shot_delay: Delay between shots (for animation)
        """
        logger.info(f"Starting full bot loop (max {max_shots} shots)...")

        # Step 1: Calibrate board
        if not self.calibrate_board():
            logger.error("Board calibration failed, cannot proceed")
            return

        # Main loop
        for shot_num in range(max_shots):
            logger.info(f"\n{'='*60}")
            logger.info(f"SHOT {shot_num + 1}/{max_shots}")
            logger.info(f"{'='*60}")

            try:
                # Capture frame before shot
                frame_before = self.capture.capture_screenshot()
                if frame_before is None:
                    logger.error("Failed to capture frame, retrying...")
                    time.sleep(1)
                    continue

                if self.debug:
                    cv2.imwrite(str(self.output_dir / f"{shot_num:02d}_before_shot.png"), frame_before)

                # Detect board state
                board = self.detect_board_state(frame_before)
                if board is None:
                    logger.warning("Board detection failed, skipping shot")
                    continue

                # Check if game is over
                pocketed = sum(1 for c in board.coins if c.pocketed)
                if pocketed >= len(board.coins):
                    logger.info(f"Game complete! All {len(board.coins)} coins pocketed.")
                    break

                # Select and execute shot
                if not self.select_and_execute_shot(board):
                    logger.warning("Shot execution failed")
                    continue

                # Wait for animation
                logger.info(f"Waiting {shot_delay}s for animation to complete...")
                time.sleep(shot_delay)

                # Capture frame after shot
                frame_after = self.capture.capture_screenshot()
                if frame_after is None:
                    logger.warning("Failed to capture post-shot frame")
                    continue

                if self.debug:
                    cv2.imwrite(str(self.output_dir / f"{shot_num:02d}_after_shot.png"), frame_after)

                # Observe outcome
                outcome = self.observe_and_compare(frame_before, frame_after)
                logger.info(f"Shot outcome: {outcome}")

                # Small delay before next shot
                time.sleep(0.5)

            except Exception as e:
                logger.error(f"Error in shot loop: {e}")
                continue

        # Final report
        logger.info(f"\n{'='*60}")
        logger.info(f"BOT FINISHED")
        logger.info(f"{'='*60}")
        logger.info(f"Total shots: {self.shot_count}")
        logger.info(f"Total coins pocketed: {self.pocketed_count}")
        if self.shot_count > 0:
            logger.info(f"Success rate: {(self.pocketed_count / self.shot_count):.1%}")


def main():
    """Entry point for full bot demo."""
    logger.info("VCore Full External Bot starting...")
    logger.info(f"Output directory: vcore_output/")

    try:
        bot = VCoreLiveBot(debug=True)
        bot.run_full_loop(max_shots=5, shot_delay=2.5)
        logger.info("Bot finished successfully")
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Bot failed: {e}")
        raise


if __name__ == "__main__":
    main()
