import os
import glob


icons = []
icons.append("icons = {}")
icons.append("")


for file in glob.glob("*.svg"):
    svg = open(f"{file}").read()
    icons.append(f"""icons['{os.path.splitext(file)[0]}'] = '''{svg}'''""")
    icons.append("")

icons_py = open("../../q2gui/q2icons.py", "w")
icons_py.write("\n".join(icons))
