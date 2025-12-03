# The light Python GUI builder (currently based on PyQt6)
Simplifying the creation of common GUI applications

## Description
q2gui is a lightweight Python GUI builder designed to simplify the creation of desktop applications using PyQt6. It provides a high-level API for building forms, menus, toolbars, tabbed interfaces, and various widgets with minimal code. Features include:
- Dynamic menu and toolbar creation with shortcuts and icons
- Form builder supporting labels, inputs, combo boxes, radio buttons, checkboxes, date/time pickers, and more
- Tabbed and split layouts, frames, and groupings
- Sheet/grid controls with customizable headers, sizes, and actions
- Built-in support for color modes (light/dark)
- Status bar, tool buttons, and message dialogs
- Easy event handling and validation logic
- Demo applications showcasing usage patterns

# How to start 
## With PyPI package:
```bash
poetry new project_01 && cd project_01 && poetry shell
poetry add q2gui
cd project_01
python -m q2gui > example_app.py && python example_app.py
```
## Explore sources:
```bash
git clone https://github.com/AndreiPuchko/q2gui.git
cd q2gui
pip3 install poetry
poetry shell
poetry install
python3 demo/demo_00.py     # All demo launcher
python3 demo/demo_01.py     # basic: main menu, form & widgets
python3 demo/demo_02.py     # forms and forms in form
python3 demo/demo_03.py     # grid form (CSV data), automatic creation of forms based on data
python3 demo/demo_04.py     # progressbar, data loading, sorting and filtering
python3 demo/demo_05.py     # nonmodal form
python3 demo/demo_06.py     # code editor
python3 demo/demo_07.py     # database app (4 tables, mock data loading) - requires a q2db package
python3 demo/demo_08.py     # database app, requires a q2db package, autoschema
```

## demo/demo_07.py screenshot
=======
![Alt text](https://andreipuchko.github.io/q2gui/screenshot.png)
# Build standalone executable 
(The resulting executable file will appear in the folder  dist/)
### One file
```bash
pyinstaller -F demo/demo.py
```

### One directory
```bash
pyinstaller -D demo/demo.py
```
