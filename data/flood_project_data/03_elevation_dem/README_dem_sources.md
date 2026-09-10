# Elevation / DEM data for Velachery–Pallikaranai–Medavakkam

I could not download actual DEM raster files directly into this folder — Bhuvan
(ISRO) requires interactive login/AOI-drawing in a browser, and this
environment's network access is restricted to package/code repositories
(github, pypi, npm, etc.), not government geoportals. Here's exactly how to
get the real files yourself, fastest option first.

## Option 1 (recommended): SRTM 30m via OpenTopography — no login, scriptable
- Portal: https://portal.opentopography.org/raster?opentopoID=OTSRTM.082015.4326.1
- Or API: `https://portal.opentopography.org/API/globaldem?demtype=SRTMGL1&south=12.90&north=13.00&west=80.18&east=80.245&outputFormat=GTiff&API_Key=YOUR_KEY`
  (free API key, instant signup at opentopography.org)
- Bounding box to use for this belt: **south=12.90, north=13.00, west=80.18, east=80.245**
- Resolution: 30m (SRTM GL1) — same order of accuracy as the CartoDEM used in
  the real Velachery SWMM study (see 02_drainage_network notes).

## Option 2: CartoDEM (ISRO Bhuvan) — matches what the real Velachery study used
- Portal: https://bhuvan-app3.nrsc.gov.in/data/download/index.php
- Requires free Bhuvan account registration.
- Select Cartosat-1 DEM, draw/select the AOI (use the bbox above), download
  the tile covering Chennai South (tile naming is by lat/lon grid — search
  "Chennai" or use the map picker).
- <cite>Accuracy: 8m LE90 (vertical), 15m CE90 (horizontal), 30m posting.</cite>

## Option 3: Copernicus GLO-30 DEM (often sharper over flat/urban terrain than SRTM)
- https://portal.opentopography.org/raster?opentopoID=OTSDEM.032021.4326.3
- Same API pattern as Option 1, demtype=`COP30`.

## Why this matters for your project specifically
The belt is extremely flat — <cite>average altitude ~5m above mean sea level
across the whole 235 km² Pallikaranai catchment</cite>, and a 2025 drone-based
study of the exact same area found <cite>DEM elevation in the 15–20m range with
only 3–8% slope</cite> at finer resolution. This means:
- **30m DEM will blur real street-level high/low points** that matter for
  block-by-block flood prediction. If you have time, get a smaller/finer DEM
  (drone photogrammetry, or even manually digitized spot heights from Google
  Earth) for just 2-3 streets in Velachery for a higher-fidelity demo patch.
- For the hackathon prototype, 30m SRTM/CartoDEM is a perfectly reasonable
  MVP baseline — just be upfront in your presentation that street-level
  accuracy would need LiDAR or drone survey in a production system.

## Suggested file naming once downloaded
Save into this folder as:
- `srtm30_velachery_pallikaranai_medavakkam.tif`
- `cartodem30_velachery_pallikaranai_medavakkam.tif` (if using Option 2)
