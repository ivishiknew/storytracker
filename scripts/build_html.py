"""
build_html.py
Reads data/app-home-merged.csv and generates index.html
with the CSV data embedded in the template.
"""

import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.join(SCRIPT_DIR, "..")
MERGED_PATH = os.path.join(ROOT_DIR, "data", "app-home-merged.csv")
TEMPLATE_PATH = os.path.join(ROOT_DIR, "template.html")
OUTPUT_PATH = os.path.join(ROOT_DIR, "index.html")


def main():
    # Read CSV
    with open(MERGED_PATH, "r") as f:
        csv_data = f.read().replace("\r\n", "\n").replace("\r", "\n")

    # Escape for JS template literal
    csv_data = csv_data.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    # Read template
    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()

    # Inject CSV
    html = template.replace("CSVPLACEHOLDER", csv_data)

    # Write output
    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    print(f"Built index.html ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
