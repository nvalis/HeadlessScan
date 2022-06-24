import argparse
import subprocess
import json
import pathlib
import datetime
import shutil
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def read_base_config(baseconfig_file):
    with open(baseconfig_file) as cf:
        base_config = json.load(cf)
    return base_config


def write_scan_config(config, out_file):
    with open(out_file, "w") as cf:
        json.dump(config, cf)
    logger.debug(f"Wrote scan config to {out_file}.")


def epsonscan2(settings_file):
    """Run: epsonscan2 -s settings.sf2"""
    subprocess.run(["epsonscan2", "-s", settings_file])
    logger.info("Scanning...")


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

    i = 0
    while True:
        i += 1
        conf_preset["FileNamePrefix"]["string"] = f"scan{i:03}"
        write_scan_config(base_config, out_file=tmp_config)
        logger.debug(f'Scanning {conf_preset["FileNamePrefix"]["string"]}.png...')
        epsonscan2(tmp_config)

    # shutil.rmtree(tmp_path)


if __name__ == "__main__":
    main()
