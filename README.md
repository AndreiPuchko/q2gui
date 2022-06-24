# The light Python GUI builder (currently based on PyQt6)

# How to start 
## With docker && x11:
```bash
git clone https://github.com/AndreiPuchko/q2gui.git
#                      sudo if necessary 
cd q2gui/docker-x11 && ./build_and_run_menu.sh
```
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
