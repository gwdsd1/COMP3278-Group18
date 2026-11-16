"""Build the standalone GitHub Pages demo into a new output directory."""

import argparse
import base64
import hashlib
import io
import json
from pathlib import Path
import runpy
import shutil
import tarfile
from urllib.request import urlopen


SOURCE = Path(__file__).resolve().parent
PROJECT = SOURCE.parent
SQLJS = "https://registry.npmjs.org/sql.js/-/sql.js-1.13.0.tgz"
SQLJS_SHA512 = "RJbVP1HRDlUUXahJ7VMTcu9Rm1Nzw+EBpoPr94vnbD4LwR715F3CcxE2G2k45PewcaZ57pjetYa+LoSJLAASgA=="


def build(output):
    with urlopen(SQLJS, timeout=20) as response:
        archive = response.read()
    digest = base64.b64encode(hashlib.sha512(archive).digest()).decode("ascii")
    if digest != SQLJS_SHA512:
        raise ValueError("sql.js download did not match the pinned SHA-512 digest")

    output.mkdir(parents=True)
    for src, dest in (
        (SOURCE / "index.html", "index.html"),
        (SOURCE / "app.js", "app.js"),
        (PROJECT / "app/style.css", "style.css"),
        (PROJECT / "app/queries.sql", "queries.sql"),
        (PROJECT / "database/app.db", "app.db"),
    ):
        shutil.copyfile(src, output / dest)
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as package:
        for member, filename in (
            ("package/dist/sql-wasm.js", "sql-wasm.js"),
            ("package/dist/sql-wasm.wasm", "sql-wasm.wasm"),
            ("package/LICENSE", "sql.js-LICENSE"),
        ):
            with package.extractfile(member) as content:
                (output / filename).write_bytes(content.read())

    offline = runpy.run_path(str(PROJECT / "app/server.py"))
    config = {key: offline[key] for key in ("FEATURES", "FIELDS", "OPTIONS", "COLUMN_NAMES", "NOTES")}
    (output / "config.json").write_text(json.dumps(config, ensure_ascii=False), encoding="utf-8")
    (output / ".nojekyll").touch()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("the output directory must not already exist")
    build(args.output)
