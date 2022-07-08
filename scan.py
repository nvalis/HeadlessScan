#!/usr/bin/env python3

import argparse
import subprocess
import json
import pathlib
import datetime
import shutil
from enum import Enum
import logging

logging.basicConfig(
    format="%(asctime)s: %(levelname)10s - %(message)s", level=logging.INFO
)
logger = logging.getLogger()


class ES2_STATUS(Enum):
    """Output mapping for epsonscan2."""
    DEVICE_NOT_FOUND = b"ERROR : Device is not found...\n"
    CONNECTION_ERROR = b"ERROR : Unable to send data. Check the connection to the scanner and try again.\n"
    UNEXPECTED_ERROR = b"ERROR : An unexpected error occurred. Epson Scan 2 will close."
    NO_DOCUMENT = b"ERROR : Load the originals in the ADF.\n"
    ALL_OKAY = b""


def read_base_config(baseconfig_file):
    with open(baseconfig_file) as cf:
        base_config = json.load(cf)
    return base_config


def write_scan_config(config, out_file):
    with open(out_file, "w") as cf:
        json.dump(config, cf)
    logger.debug(f"Wrote scan config to {out_file}.")


def epsonscan2(settings_file):
    """Run epsonscan2"""
    logger.info("Scanning...")
    proc = subprocess.Popen(["epsonscan2", "-s", settings_file], stdout=subprocess.PIPE)
    stdout, _ = proc.communicate()
    logger.debug(f'epsonscan2 returned: "{str(stdout)}"')
    return stdout


def convert_scans_to_pdf(tmp_path, out_file):
    subprocess.run(
        ["convert", "-adjoin", str(tmp_path / pathlib.Path("scan*.png")), out_file]
    )


def main():
    parser = argparse.ArgumentParser(description="Scan multipage documents.")
    parser.add_argument(
        "-t",
        "--timeout",
        type=float,
        default=10.0,
        help="Scanning timeout to end current document.",
    )
    parser.add_argument("settingsfile", help="Base settings file to use for scanning.")
    args = parser.parse_args()

    now = datetime.datetime.now()
    tmp_path = pathlib.Path(f"./scan_{now.strftime('%Y%m%d_%H%M%S')}/")
    tmp_path.mkdir()
    tmp_config = tmp_path / pathlib.Path("settings.sf2")

    base_config = read_base_config(pathlib.Path(args.settingsfile))
    conf_preset = base_config["Preset"][0]["0"][0]
    conf_preset["UserDefinePath"]["string"] = str(tmp_path)

    page = 1
    scanning = True
    while scanning:
        conf_preset["FileNamePrefix"]["string"] = f"scan{page:03}"
        write_scan_config(base_config, out_file=tmp_config)
        logger.debug(f'Scanning {conf_preset["FileNamePrefix"]["string"]}.png...')
        stdout = epsonscan2(tmp_config)

        if stdout == ES2_STATUS.ALL_OKAY.value:
            logger.info(
                f'Successfully scanned {conf_preset["FileNamePrefix"]["string"]}'
            )
            page += 1
        elif stdout == ES2_STATUS.DEVICE_NOT_FOUND.value:
            logger.error("Scanner device not found!")
        elif stdout == ES2_STATUS.CONNECTION_ERROR.value:
            logger.error("Connection error to scanner!")
        elif stdout == ES2_STATUS.UNEXPECTED_ERROR.value:
            logger.error("epsonscan2 unexpectedly closed")
        elif stdout == ES2_STATUS.NO_DOCUMENT.value:
            logger.warning("No document in scanner...")
        else:
            logger.critical(f'Unknown epsonscan2 status: "{str(stdout)}"')
            page += 1
        if page >= 3:  # TODO: read button input to stop
            scanning = False

    convert_scans_to_pdf(tmp_path, f"scan_{now.strftime('%Y%m%d_%H%M%S')}.pdf")
    shutil.rmtree(tmp_path)


if __name__ == "__main__":
    main()
