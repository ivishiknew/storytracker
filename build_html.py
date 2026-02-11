"""
build_html.py
Reads data/app-home-merged.csv and generates index.html
with the CSV data embedded in the template.
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
MERGED_PATH = os.path.join(ROOT_DIR, "data", "app-home-merged.csv")
TEMPLATE_PATH = os.path.join(ROOT_DIR, "template.html")
OUTPUT_PATH = os.path.join(ROOT_DIR, "index.html")


def main():
    with open(MERGED_PATH, "r") as f:
        csv_data = f.read().replace("\r\n", "\n").replace("\r", "\n")

    csv_data = csv_data.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${")

    with open(TEMPLATE_PATH, "r") as f:
        template = f.read()

    html = template.replace("CSVPLACEHOLDER", csv_data)

    with open(OUTPUT_PATH, "w") as f:
        f.write(html)

    print(f"Built index.html ({len(html):,} bytes)")


if __name__ == "__main__":
    main()
