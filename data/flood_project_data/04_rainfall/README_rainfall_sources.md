# Rainfall / nowcast data for this belt

## Included in this folder
- `sample_rainfall_event_SYNTHETIC.csv` — a synthetic 6-hour, 15-minute-interval
  rainfall burst (~168mm total) you can use to drive your demo pipeline end
  to end (rainfall input -> surface routing -> drainage graph -> alert) before
  you've wired up a live feed. Loosely scaled to match real documented
  monsoon burst magnitudes for this region (see below) — NOT a real recorded
  event, clearly a stand-in.

## Real sources — no login/scriptable
| Source | What you get | How |
|---|---|---|
| **NASA GPM IMERG** | Half-hourly satellite rainfall estimate, ~10km grid, global, free | `https://gpm.nasa.gov/data/imerg` or via Google Earth Engine (`NASA/GPM_L3/IMERG_V07`). Good for **backtesting** your model against 2015/2020/2021/2023 flood dates. |
| **NASA PMM Publisher API** | 30-min/1-day/7-day precipitation + flood/landslide "nowcast" layers as GeoJSON/SHP/TIF | `https://gpm.nasa.gov/data/visualization/precip-apps` |
| **IMD AWS/ARG station data** | Real ground-station rainfall, but only the **last 7 days** are exposed publicly | mausam.imd.gov.in (scrape-only, no clean API); see community script `github.com/craigdsouza/getRainfallData` for a working scraper pattern |
| **IMD Doppler Radar - Chennai (Nungambakkam)** | Live radar reflectivity images (not raw data / not an API) | `https://mausam.imd.gov.in/responsive/radar.php?id=Chennai` — image only; true radar nowcast products aren't exposed publicly. For your "Doppler radar nowcast" input layer, you'll likely need to **simulate** this for the demo, and describe the real integration path in your presentation (NCMRWF/IMD would provide this operationally). |

## Real regional rainfall context to cite in your report
- Pallikaranai catchment (which covers this whole belt) receives about
  **1,300 mm annual rainfall**, concentrated in the Oct–Nov northeast monsoon.
- During Cyclone Michaung (Dec 2023), Chennai's Nungambakkam and Meenambakkam
  stations recorded **52–53 cm of rain between Dec 2–4** — an extreme
  multi-day total, useful as your "worst-case stress test" scenario.
- The peer-reviewed Velachery SWMM study used **daily IMD rainfall from
  1975–2015** to build Intensity-Duration-Frequency (IDF) curves for 2, 5,
  10, 50, and 100-year return periods — if you can get that IDF table (from
  the paper or by requesting it from RMC Chennai/IMD), it's your best proxy
  for "what rainfall rate actually overwhelms this drainage network," which
  you need for your risk-scoring thresholds.

## Suggested next step
For the hackathon demo, wire your pipeline to accept **either** the included
synthetic CSV **or** a live IMD/GPM feed via a simple adapter — this lets you
demo reliably regardless of network access on presentation day.
