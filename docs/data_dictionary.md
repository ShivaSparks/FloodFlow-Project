# FloodFlow Stage 1 data dictionary

## Provenance

Every future processed dataset must carry or be associated with:

- `source_type`: `real`, `synthetic`, or `simulated`
- `source_name`
- `source_timestamp` when available
- `confidence` when the value is an estimate or forecast

## Spatial convention

- Input and display CRS: EPSG:4326 (WGS84)
- Pilot bbox: south 12.90, north 13.00, west 80.18, east 80.245
- Raw full-Chennai flood files may extend outside the pilot bbox.

## Core records

### Flood history

`osm_id`, `road_type`, `is_flooded`, `source_file`, `lon`, `lat`.
This is observed historical information, not a forecast.

### Drainage nodes and edges

Nodes use `node_id`, location, elevations, type, and notes. Edges use
`edge_id`, `from_node`, `to_node`, pipe dimensions, slope, condition, and
`design_capacity_cumecs`. The current drainage files are synthetic and have
explanatory comment rows; Stage 1 removes those rows in processed copies.

### Rainfall nowcast

`issued_at`, `valid_time`, `lead_minutes`, `zone_id`,
`observed_mm_15min`, `forecast_mm_15min`, `source_type`, `confidence`.

### Prediction output

Future model outputs should include `forecast_time`, `road_id` or cell ID,
`predicted_depth_cm`, `risk_level`, `drainage_utilization`, `confidence`, and
`is_synthetic`.
