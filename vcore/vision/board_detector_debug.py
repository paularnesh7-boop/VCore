#!/usr/bin/env python3
"""
Board Detection Deep Dive

Detailed step-by-step board detection with visualizations.
Useful for debugging and calibration.
"""

import logging
import cv2
import numpy as np
from pathlib import Path
from typing import Optional, Tuple

from vcore.capture.screen_capture import ScreenCapture, ScreenAnalyzer

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger('VCore.BoardDetection')


class DebugBoardDetector:
    """
    Enhanced board detector with visualization and debugging output.
    Shows intermediate detection steps for calibration.
    """

    def __init__(self, output_dir: str = "board_detection_debug"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.analyzer = ScreenAnalyzer()
        logger.info(f"DebugBoardDetector initialized, output: {self.output_dir}")

    def detect_with_visualization(self, frame: np.ndarray) -> Optional[dict]:
        """
        Perform board detection with step-by-step visualization.
        """
        logger.info("Starting board detection with visualization...")
        step = 0

        # Step 1: Save original frame
        step += 1
        cv2.imwrite(str(self.output_dir / f"{step:02d}_original.png"), frame)
        logger.info(f"Step {step}: Original frame saved")

        # Step 2: Extract game region
        step += 1
        game_region = self.analyzer.get_game_region(frame)
        if game_region is not None:
            cv2.imwrite(str(self.output_dir / f"{step:02d}_game_region.png"), game_region)
            logger.info(f"Step {step}: Game region extracted")
        else:
            logger.warning(f"Step {step}: Failed to extract game region")
            return None

        # Step 3: Convert to grayscale
        step += 1
        gray = cv2.cvtColor(game_region, cv2.COLOR_BGR2GRAY)
        cv2.imwrite(str(self.output_dir / f"{step:02d}_grayscale.png"), gray)
        logger.info(f"Step {step}: Converted to grayscale")

        # Step 4: Edge detection
        step += 1
        edges = cv2.Canny(gray, 50, 150)
        cv2.imwrite(str(self.output_dir / f"{step:02d}_edges.png"), edges)
        logger.info(f"Step {step}: Edge detection (Canny)")

        # Step 5: Detect board corners
        step += 1
        corners = self._detect_corners_debug(edges, game_region)
        if corners:
            logger.info(f"Step {step}: Board corners detected: {corners}")
        else:
            logger.warning(f"Step {step}: Failed to detect board corners")
            return None

        # Step 6: Detect coins
        step += 1
        coins = self._detect_coins_debug(game_region)
        logger.info(f"Step {step}: Detected {len(coins)} coins")

        # Step 7: Detect pockets
        step += 1
        pockets = self._detect_pockets_debug(game_region)
        logger.info(f"Step {step}: Detected {len(pockets)} pockets")

        # Final: Draw detections on frame
        step += 1
        annotated = self._draw_detections(game_region, corners, coins, pockets)
        cv2.imwrite(str(self.output_dir / f"{step:02d}_final_detection.png"), annotated)
        logger.info(f"Step {step}: Final detection visualization")

        board_data = {
            'width': float(game_region.shape[1]),
            'height': float(game_region.shape[0]),
            'corners': corners,
            'coins': coins,
            'pockets': pockets,
        }

        logger.info(f"Board detection complete: {board_data}")
        return board_data

    def _detect_corners_debug(self, edges: np.ndarray, frame: np.ndarray) -> Optional[Tuple]:
        """
        Detect board corners with debug output.
        """
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        logger.debug(f"Found {len(contours)} contours")

        if not contours:
            return None

        # Find largest contour
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)
        logger.debug(f"Largest contour area: {area}")

        # Approximate as quadrilateral
        epsilon = 0.02 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)

        if len(approx) != 4:
            logger.warning(f"Expected 4 corners, got {len(approx)}")
            return None

        pts = approx.reshape(4, 2)
        pts = sorted(pts, key=lambda p: (p[1], p[0]))

        top_left, top_right = sorted(pts[:2], key=lambda p: p[0])
        bottom_left, bottom_right = sorted(pts[2:], key=lambda p: p[0])

        corners = (tuple(top_left), tuple(top_right), tuple(bottom_left), tuple(bottom_right))
        logger.debug(f"Board corners: {corners}")
        return corners

    def _detect_coins_debug(self, frame: np.ndarray) -> list:
        """
        Detect coins with debug output.
        """
        coins = []
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Test each color
        color_ranges = {
            'black': [(np.array([0, 0, 0]), np.array([180, 255, 100]))],
            'red': [
                (np.array([0, 100, 100]), np.array([10, 255, 255])),
                (np.array([170, 100, 100]), np.array([180, 255, 255]))
            ],
            'white': [(np.array([0, 0, 200]), np.array([180, 30, 255]))],
        }

        for color_name, ranges in color_ranges.items():
            for i, (lower, upper) in enumerate(ranges):
                mask = cv2.inRange(hsv, lower, upper)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
                mask = cv2.dilate(mask, kernel, iterations=2)

                circles = cv2.HoughCircles(
                    mask,
                    cv2.HOUGH_GRADIENT,
                    dp=1,
                    minDist=20,
                    param1=50,
                    param2=30,
                    minRadius=8,
                    maxRadius=20
                )

                if circles is not None:
                    count = len(circles[0])
                    logger.debug(f"Color '{color_name}' range {i}: {count} circles detected")
                    for (x, y, radius) in circles[0]:
                        coins.append({
                            'id': f"{color_name}_{len(coins)}",
                            'x': float(x),
                            'y': float(y),
                            'radius': float(radius),
                            'color': color_name,
                            'is_striker': color_name == 'white'
                        })

        logger.debug(f"Total coins detected: {len(coins)}")
        return coins

    def _detect_pockets_debug(self, frame: np.ndarray) -> list:
        """
        Detect pockets with debug output.
        """
        pockets = []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, dark = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY)

        circles = cv2.HoughCircles(
            dark,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=100,
            param1=50,
            param2=20,
            minRadius=10,
            maxRadius=25
        )

        if circles is not None:
            logger.debug(f"Detected {len(circles[0])} pockets")
            for (x, y, r) in circles[0]:
                pockets.append({'x': float(x), 'y': float(y)})
        else:
            logger.debug("No pockets detected")

        return pockets

    def _draw_detections(self, frame: np.ndarray, corners: Tuple, coins: list, pockets: list) -> np.ndarray:
        """
        Draw all detections on frame.
        """
        annotated = frame.copy()

        # Draw board boundary
        if corners:
            corner_array = np.array(corners, dtype=np.int32)
            cv2.polylines(annotated, [corner_array], True, (0, 255, 0), 3)
            for i, corner in enumerate(corners):
                cv2.circle(annotated, corner, 8, (0, 255, 0), -1)
                cv2.putText(annotated, f"C{i}", corner, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Draw coins
        for coin in coins:
            center = (int(coin['x']), int(coin['y']))
            radius = int(coin['radius'])
            color = {
                'black': (50, 50, 50),
                'red': (0, 0, 255),
                'white': (255, 255, 255)
            }.get(coin['color'], (128, 128, 128))
            cv2.circle(annotated, center, radius, color, 2)
            label = "S" if coin.get('is_striker') else coin['id'][-1]
            cv2.putText(annotated, label, center, cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Draw pockets
        for pocket in pockets:
            center = (int(pocket['x']), int(pocket['y']))
            cv2.circle(annotated, center, 15, (100, 100, 100), 3)

        return annotated


def main():
    """Debug board detection from live screen."""
    logger.info("Starting board detection debug...")

    try:
        capture = ScreenCapture()
        detector = DebugBoardDetector()

        # Capture frame
        frame = capture.capture_screenshot()
        if frame is None:
            logger.error("Failed to capture screen")
            return

        # Run detection with visualization
        board_data = detector.detect_with_visualization(frame)

        if board_data:
            logger.info("Board detection successful!")
            logger.info(f"Output saved to: {detector.output_dir}/")
        else:
            logger.error("Board detection failed")

    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
