from pathlib import Path

import geopandas as gpd
import pandas as pd
import rasterio

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "flood_project_data"


def test_real_flood_history_is_present():
    frame = gpd.read_file(DATA / "01_flood_history" / "flood_history_velachery_pallikaranai_medavakkam.geojson")
    assert len(frame) == 2167
    assert frame.geometry.geom_type.isin(["LineString", "MultiLineString"]).all()


def test_synthetic_drainage_csvs_have_valid_ids_and_references():
    nodes = pd.read_csv(DATA / "02_drainage_network" / "drainage_nodes_SYNTHETIC.csv", comment="#")
    edges = pd.read_csv(DATA / "02_drainage_network" / "drainage_edges_SYNTHETIC.csv", comment="#")
    assert nodes["node_id"].astype(str).str.fullmatch(r"N\d+").all()
    assert edges["edge_id"].astype(str).str.fullmatch(r"E\d+").all()
    assert set(edges["from_node"]).union(edges["to_node"]).issubset(set(nodes["node_id"]))


def test_synthetic_dem_has_expected_grid():
    with rasterio.open(DATA / "03_elevation_dem" / "synthetic_dem_100m.asc") as dataset:
        assert dataset.width == 20
        assert dataset.height == 20
        assert dataset.count == 1


def test_synthetic_nowcast_has_forecast_values():
    rainfall = pd.read_csv(DATA / "04_rainfall" / "synthetic_nowcast_3h.csv")
    assert rainfall["forecast_mm_15min"].notna().all()
    assert rainfall["lead_minutes"].max() == 165
