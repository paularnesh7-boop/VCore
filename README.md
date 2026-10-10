# VCore

VCore is a prototype automated carrom-playing system that combines a simplified computer vision layer, a shot-selection engine, a trajectory/physics sim, and an execution controller. The goal is to provide a reusable architecture for automated decision-making and to validate the underlying calculations in a local simulation rather than relying on fake "successful" outcomes.

## What is included

- Board and coin state modeling for a carrom board simulation
- A lightweight perception layer that recognizes board geometry and object positions from structured state data
- Candidate shot generation and scoring for pocketing opportunities
- Physics-based collision and shot execution simulation
- An execution feedback loop that refines the next decision based on observed results
- Diagnostic logging and automated tests for core functionality
- A dark-purple premium UI mockup for the VCore control surface

## Repository structure

- `vcore/` — core Python logic
- `tests/` — validation tests
- `app/` — static UI mockup
- `examples/` — local demo entry points

## Quick start

1. Create a virtual environment if desired.
2. Install the package in editable mode:

   python -m pip install -e .

3. Run the demonstration:

   python -m examples.demo

4. Run the automated tests:

   python -m unittest discover -s tests -v

## Core architecture

### 1. Vision

The vision layer is intentionally modular. It does not depend on the decision engine or executor. It receives structured board information and returns a normalized board state with boundaries, pockets, striker, and coin positions.

### 2. Decision engine

The decision engine generates candidate shots from every coin to every pocket, calculates hit geometry, and ranks the result by expected value.

### 3. Physics and trajectory prediction

Physics simulation computes the actual movement of the striker and impacted coins based on a simplified collision model, friction, and pocket detection.

### 4. Execution feedback loop

The controller performs an action, observes the board state, compares the result to the prediction, and updates the next decision. This keeps the system stateful and testable.

## Validation

The repository includes automated tests for:

- object board detection normalization
- strategic shot ranking
- collision and momentum behavior
- shot execution and feedback loop completion

## Limitations

This repository intentionally provides a validated local simulation and architecture prototype, not a production-grade real-world carrom vision stack. Real image recognition, camera calibration, ball tracking, and hardware execution would require a separate sensor and control implementation. The logic in this codebase is designed to be testable and extensible rather than pretending to have solved full tabletop robotics.

## License

MIT
