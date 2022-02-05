import os
import webbrowser
import pyperclip
from cowidev.vax.cmd.utils import get_logger
from cowidev.megafile.generate import generate_megafile
from cowidev.utils import paths

logger = get_logger()


def main_export(url):
    main_source_table_html(url)
    main_megafile()


def main_source_table_html(url):
    # Read html content
    print("-- Reading HTML table... --")
    path = os.path.join(paths.SCRIPTS.OUTPUT_VAX, "source_table.html")
    with open(path, "r") as f:
        html = f.read()
    logger.info("Redirecting to owid editing platform...")
    pyperclip.copy(html)
    webbrowser.open(url)


def main_megafile():
    """Executes scripts/scripts/megafile.py."""
    print("-- Generating megafiles... --")
    generate_megafile()
