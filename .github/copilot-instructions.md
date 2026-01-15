# Copilot Instructions for V

## Project Overview
- This project is a simple interactive 7x7 grid GUI built with Tkinter (see `interactive_grid.py`).
- The main entry point is the `InteractiveGrid` class, which creates a window with a clickable grid. Clicking a cell highlights it in red.

## Architecture & Patterns
- All logic is contained in a single file: `interactive_grid.py`.
- The grid size and cell size are defined by the constants `GRID_SIZE` and `CELL_SIZE` at the top of the file.
- The grid is drawn using the `draw_grid()` method, which colors cells in a checkerboard pattern and highlights the selected cell.
- User interaction is handled by the `on_click()` method, which updates the selected cell and redraws the grid.

## Developer Workflows
- **Run the app:** Execute `python interactive_grid.py` to launch the GUI.
- **No build or test scripts** are present; the project is run directly as a Python script.
- **No external dependencies** beyond the Python standard library (Tkinter).

## Conventions
- All code is in a single file; no modules or packages.
- No type annotations or docstrings are used.
- No custom error handling or logging is implemented.

## Extending the Project
- Add new features by extending the `InteractiveGrid` class or adding new methods.
- For additional files or modules, update this document to reflect new patterns or workflows.

## References
- Main logic: [`interactive_grid.py`](../interactive_grid.py)
- No other key files or directories at this time.

---
_If you add new files, workflows, or conventions, update this document to help future AI agents and developers._
