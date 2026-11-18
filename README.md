# The World, Mapped — 18 November 2026

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/kinoy-1/news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/kinoy-1/news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

Entry for the [make.fun bounty "Sum up 18 November's world news in one image"](https://make.fun/c/news-image-20261118).

## The image

`entry.png` is a 1024×1024 editorial infographic, drawn by `draw.py`
(pure Python/PIL, deterministic — no photographs, no generated imagery).
It sums up Wednesday 18 November 2026 in 35 stories across 6 continents,
as reported that day:

**The map is the hero:** a dot-matrix world map carries 9 numbered pins
for the 9 biggest stories, instead of the small map at the foot of the
page that the winning entries used.

1. **US–Iran trade fire over Bahrain and Qeshm** — US jets hit an IRGC
   missile site on Qeshm; Iran fired drones at Bahrain. All intercepted.
2. **A span of the Crimea bridge falls into the sea** — Ukrainian drones
   and missiles destroyed a Kerch road span; two were killed.
3. **Trump meets Marcos, then flies to Shenzhen** — a first Xi–Putin
   trilateral is set for Thursday at the APEC summit.
4. **Nvidia's revenue doubles to $115.8bn** — Q3 sales up 103%, the first
   $100bn-plus quarter; EPS $2.68 beat $2.47.
5. **Wall Street slides as the Dow drops 849** — down 1.64% to 50,759,
   a fourth straight day of losses.
6. **Cyclone Akvan bears down on Andhra Pradesh** — landfall Friday with
   gusts to 145 km/h.
7. **Japan scrambles jets as Russian planes enter** — two Russian aircraft
   suspected near Okinoshima; Seoul and Taipei also responded.
8. **APEC opens in Shenzhen with Xi keynote** — leaders of 21 Pacific
   economies meet 18–19 November.
9. **Houthis launch drones at Saudi pipeline** — five drones at two pump
   stations on the East–West pipeline near Riyadh.

Plus a "By the numbers" strip ($115.8bn · −849 · 145 km/h · 3rd) and 26
more stories, from the Knesset speaker vote (66–52) to COP31's finance
deadlock and Fiji's El Niño disaster declaration.

Sources: Reuters, Associated Press, BBC, Barron's, IMD, RFE/RL — events
of 18 November 2026.

## How it runs

`main.py` (Python 3.13, standard library only) copies `entry.png` to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`). The output is
byte-identical on every run — verified: two runs, identical sha256.

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

`draw.py` regenerates `entry.png` from scratch (same bytes every run).

## License

MIT — see `LICENSE`.

---

Referral code: qzezv1jd
