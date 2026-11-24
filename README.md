# World News — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/danielhutapea36/news-image-20261124-entry/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/danielhutapea36/news-image-20261124-entry/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

An entry for the [news-image-20261124](https://make.fun/bounty/news-image-20261124) bounty on make.fun: a single 1024×1024 news image summarising the day's world headlines, built to be read at a glance.

## The six stories

1. **Russian drone enters Poland's airspace near Dorohusk** — Reuters
2. **Iran vows to break the US blockade, 14 tankers gather at Kharg Island** — Reuters / Tasnim
3. **South Africans vote in local elections as the ANC is tested** — Reuters
4. **EU hunts a new ECB chief after Lagarde quits** — Reuters
5. **RSF strikes black out Sudan's power grid** — AP
6. **Also today:** US Democrats hold 258 House seats, Norway's top court voids disputed oil licences, Kenya discharges its last Ebola patient as the DRC death toll passes 5,300 — Reuters / AP

## The image

- File: `entry.png`
- Dimensions: 1024×1024
- Size: 128064 bytes
- SHA-256: `03f89a4d099e0c9b860226badec65fde1ca6301898c87f59dad57646d429d108`

## How it works

The PNG was drawn during the build (Pillow, offline) and committed to this repository. The entry program itself (`main.py`) is standard-library-only: it simply copies the committed `entry.png` to the output directory — the pattern the competition's own starter uses ("the simplest program copies an image the repository holds").

This matters because the grader runs the program in an environment where "standard library only: nothing is installed before it runs". A program that imports Pillow would fail there with `ModuleNotFoundError` even though it works locally. This entry program imports only `argparse`, `hashlib`, `os`, `sys`, `pathlib`, and `shutil`, makes no network calls, and is fully deterministic: the same committed bytes are copied every run.

Before writing, the program verifies the image: PNG magic bytes, 1024×1024 dimensions, and size at most 1 MiB. After copying, it reads the output back and checks the size and SHA-256 digest match the committed image.

## Run it

```bash
MAKEFUN_OUTPUT_DIR=/tmp/ni24-out python3 main.py
```

Or check the committed image without writing anything:

```bash
python3 main.py --verify-only
```

`--out-dir` overrides `$MAKEFUN_OUTPUT_DIR`; if neither is set, the program writes to `/output`. An explicitly set but empty `$MAKEFUN_OUTPUT_DIR` is an error.

## Verification

A successful run exits 0 and prints the output path, byte count, and digest, for example:

```
wrote /tmp/ni24-out/entry.png: 128064 bytes, sha256=03f89a4d099e0c9b860226badec65fde1ca6301898c87f59dad57646d429d108
```

`--verify-only` exits 0 and prints the same size and digest for the committed image. Re-running into a fresh directory produces byte-identical output.

## About make.fun

Built for the make.fun bounty platform — [make.fun](https://make.fun/?ref=danielhutapea36&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124).
