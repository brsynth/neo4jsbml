# Load file and sanitize molecule

import argparse
import os
import re
import subprocess
import tempfile
from typing import List


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--input-specification-pdf",
        required=True,
        help="Path of the specification file, .pdf",
    )
    parser.add_argument(
        "-o",
        "--output-specification-txt",
        required=True,
        help="Path of the specification file, .txt",
    )

    args = parser.parse_args()

    finput = args.input_specification_pdf
    foutput = args.output_specification_txt

    if not os.path.isfile(finput):
        parser.error("File does not exist: %s" % (finput,))

    # pdf2ps
    tmp = tempfile.NamedTemporaryFile(suffix=".ps")
    cmd = ["pdf2ps", finput, tmp.name]
    subprocess.run(cmd, capture_output=True, encoding="utf8")

    # ps2ascii
    cmd = ["ps2ascii", tmp.name]
    ret = subprocess.run(cmd, capture_output=True, encoding="utf8")
    data = ret.stdout

    with open(foutput, "w") as fod:
        for line in data.split("\n"):
            data = line[17:]
            data = re.sub(r"\d+$", "", data)
            data = re.sub(r"\s+$", "", data)
            fod.write(data + "\n")
    # clean
    tmp.close()
