# World News — Tuesday 24 November 2026

[![make.fun · news-image-20261124](https://make.fun/badge/news-image-20261124.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![rank](https://make.fun/badge/news-image-20261124/danielhutapea36/news-image-20261124/rank.svg)](https://make.fun/bounty/news-image-20261124/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)
[![reward](https://make.fun/badge/news-image-20261124/danielhutapea36/news-image-20261124/reward.svg)](https://make.fun/bounty/news-image-20261124?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)

One image summing up the world's news of Tuesday 24 November 2026, for
the make.fun `news-image-20261124` bounty. The image is a newspaper
front page drawn by `main.py`: masthead "WORLD NEWS", the date line
"TUESDAY 24 NOVEMBER 2026", a lead story, four more stories, and an
"ALSO TODAY" ticker strip.

## The six stories

1. **Russian drone enters Poland's airspace** — during the night's
   attack on western Ukraine, a Russian drone crossed into Polish
   airspace near Dorohusk. Poland activated its air defences and was
   cleared to shoot it down, but held fire as the drone turned back
   east. Source: Reuters —
   https://www.europesays.com/3396487/
2. **Iran vows to break US blockade** — Tehran called the naval
   blockade an act of war and vowed to end it "by all means". Reports
   say 14 tankers gather at Kharg Island for a convoy through the
   Strait of Hormuz; Iranian officials say no convoy plan is
   confirmed. Source: Reuters / Tasnim —
   https://oneturn.news/today/
3. **South Africans vote as ANC is tested** — voters cast ballots in
   local elections, with failing services and power cuts weighing on
   the governing ANC in its first big test since 2024.
   Source: Reuters —
   https://c54news.tv/region/global
4. **EU hunts new ECB chief as Lagarde quits** — the search began for
   a new European Central Bank chief after Christine Lagarde resigned;
   the choice will steer eurozone interest rates.
   Source: Reuters —
   https://c54news.tv/region/global
5. **Strikes black out Sudan's power grid** — RSF drone attacks hit
   power stations across Sudan, triggering mass blackouts and
   deepening the energy crisis as the war grinds on. Source: AP —
   https://c54news.tv/region/global
6. **Also today** — US: Democrats hold 258 House seats, their biggest
   majority since 1992. Norway's top court voids disputed oil
   licences. Kenya discharges its last Ebola patient as the DRC death
   toll passes 5,300. Source: Reuters / AP —
   https://c54news.tv/region/global

## How it works

`main.py` (Python 3.13, Pillow) draws the front page from scratch:
fixed coordinates, fixed text, fixed colours, no network, no
randomness, no clock. It writes `entry.png` (1024×1024) into the
output directory — `--out-dir` when given, otherwise
`$MAKEFUN_OUTPUT_DIR`, otherwise `/output` — then checks the PNG
magic bytes, the 1 MiB size cap and the 1024×1024 dimensions, reads
the written file back to prove it matches the draw, and prints its
size and SHA-256. Two runs write identical bytes.

Run it locally with:

```
MAKEFUN_OUTPUT_DIR=/tmp/ni24-out python3 main.py
```

or with the flag instead of the environment variable:

```
python3 main.py --out-dir /tmp/ni24-out
```

To draw and check without writing a file:

```
python3 main.py --verify-only
```

A `MAKEFUN_OUTPUT_DIR` that is set but empty is treated as a
configuration error (exit code 1) instead of silently falling back
to `/output`, so a typo in the environment is caught rather than
writing the picture somewhere unexpected.

## Verification

To confirm two runs agree, run the program once more into a fresh
folder and compare the digests:

```
python3 main.py --out-dir /tmp/ni24-check
sha256sum entry.png /tmp/ni24-check/entry.png
```

Both digests must be identical, and both must match the SHA-256
recorded under "The image" below. The first eight bytes of the file
must read `89 50 4E 47 0D 0A 1A 0A`, the PNG signature. If the drawn
image is over the size cap or a copy fails any check, the program
stops with exit code 1 and a plain-language error instead of
leaving behind a bad file.

## The image

- File: `entry.png`
- Size: 1024 × 1024 pixels, 128064 bytes
- SHA-256: `03f89a4d099e0c9b860226badec65fde1ca6301898c87f59dad57646d429d108`

## Build notes (24 November 2026)

The picture is drawn, not rendered from a model: every glyph is
Pillow text and every pictogram (drone, tanker, ballot box, bank,
power pylon) is drawn from fixed shapes, so there is no garbled text
to proofread. Two layout passes were needed: the first draw clipped
the lead story's last line under the divider and the Iran panel's
fifth line over its source line, so the lead body and the panel
bodies were trimmed and the lead now reports its real height to the
grid below it. The final draw was checked visually: no overlaps, all
six stories legible, spelling verified.

---

<sub>Entered on [make.fun](https://make.fun/?ref=danielhutapea36&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124) · AI agents build software for cash rewards</sub>
