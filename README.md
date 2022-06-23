# EndlessScan
Small utility for endless scanning of documents designed for headless use to integrate into paperless-ng.

## Requirements
This script makes use of [epsonscan2](https://support.epson.net/linux/en/epsonscan2.php) (es2).

## Config file
The file [`settings.json`](settings.json) serves as a base config file which is used to run es2. It's adopted to my my Epson ES-50 scanner. With other hardware you might have to create your own config file using `epsonscan2 -c`.

The base config can be modified using the es2 GUI:
```bash
mv settings.json settings.sf2 && epsonscan2 -e settings.sf2 && mv settings.sf2 settings.json
```
