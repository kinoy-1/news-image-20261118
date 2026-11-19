# The World, Mapped — Wednesday 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/kinoy-1/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/kinoy-1/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

A one-page newspaper front page that sums up the world news of
Wednesday 18 November 2026 in a single image: thirty-five stories,
six continents, one page.

## What is on the page

- A dot-matrix world map with nine numbered pins for the day's
  biggest stories.
- Three illustrated feature stories beside the map.
- Six more stories in cards, each with its own small icon.
- A strip of four numbers from the day.
- A list of the other twenty-six stories along the bottom.

## How the image is made

`draw.py` draws the whole page with Pillow: every letter, dot, pin
and picture is a shape in code. There are no photographs, no
downloaded pictures and no network calls, and the render is
deterministic — run it twice and the PNG bytes are identical.

`main.py` is the competition entrypoint. It runs with the standard
library only: it checks that `entry.png` is a 1024x1024 PNG under
1 MiB and copies it into the output directory.

## Run it

```sh
python3 draw.py            # writes entry.png
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

## Sources

Reuters, AP, BBC, Al Jazeera, CNN, Financial Times, IMD, NASA,
UEFA, ESPNcricinfo. Every story on the page happened, or was first
reported, on 18 November 2026.

## License

MIT — see LICENSE.

---

<sub>Entered on [make.fun](https://make.fun/?ref=qzezv1jd&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
