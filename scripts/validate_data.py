"""Validate the FloodFlow prototype data pack without modifying source files."""

from __future__ import annotations

import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import rasterio
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA_ROOT = ROOT / "data" / "flood_project_data"
PROCESSED_ROOT = ROOT / "data" / "processed"
BBOX = (12.90, 13.00, 80.18, 80.245)  # south, north, west, east


def provenance(path: Path) -> str:
    name = path.name.lower()
    rel = path.relative_to(DATA_ROOT).as_posix().lower()
    if "synthetic" in name or "synthetic" in rel:
        return "synthetic"
    if rel.startswith(("01_flood_history/", "05_roads_boundaries/", "06_known_flood_hotspots/")):
        return "real"
    if path.suffix.lower() in {".py", ".md"}:
        return "reference"
    return "unknown"


def result(path: Path, kind: str, status: str, **details: Any) -> dict[str, Any]:
    return {"file": path.relative_to(ROOT).as_posix(), "kind": kind, "provenance": provenance(path), "status": status, **details}


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_csv(path: Path) -> dict[str, Any]:
    try:
        rows = csv_rows(path)
        return result(path, "csv", "ok", rows=len(rows), columns=list(rows[0].keys()) if rows else [])
    except Exception as exc:
        return result(path, "csv", "error", error=str(exc))


def validate_geojson(path: Path) -> dict[str, Any]:
    try:
        frame = gpd.read_file(path)
        assumed_crs = frame.crs is None
        if assumed_crs:
            frame = frame.set_crs("EPSG:4326", allow_override=True)
        frame = frame.to_crs("EPSG:4326")
        bounds = tuple(float(value) for value in frame.total_bounds)
        invalid = int((~frame.geometry.is_valid.fillna(False)).sum())
        allow_outside = "_raw_full_chennai_source" in path.as_posix()
        south, north, west, east = BBOX
        inside = allow_outside or (bounds[0] >= west and bounds[2] <= east and bounds[1] >= south and bounds[3] <= north)
        status = "error" if invalid else "warning" if assumed_crs or not inside else "ok"
        return result(path, "geojson", status, features=len(frame), geometry_types=sorted(frame.geometry.geom_type.dropna().unique().tolist()), source_crs=str(frame.crs), crs_assumed=assumed_crs, bounds=list(bounds), inside_pilot_bbox=inside, invalid_geometries=invalid)
    except Exception as exc:
        return result(path, "geojson", "error", error=str(exc))


def validate_dem(path: Path) -> dict[str, Any]:
    try:
        with rasterio.open(path) as dataset:
            bounds = dataset.bounds
            return result(path, "raster", "warning" if provenance(path) == "synthetic" else "ok", driver=dataset.driver, width=dataset.width, height=dataset.height, count=dataset.count, crs=str(dataset.crs), resolution=list(dataset.res), bounds=[bounds.left, bounds.bottom, bounds.right, bounds.top], nodata=dataset.nodata)
    except Exception as exc:
        return result(path, "raster", "error", error=str(exc))


def validate_domain_files(report: dict[str, Any]) -> None:
    node_path = DATA_ROOT / "02_drainage_network" / "drainage_nodes_SYNTHETIC.csv"
    edge_path = DATA_ROOT / "02_drainage_network" / "drainage_edges_SYNTHETIC.csv"
    if node_path.exists() and edge_path.exists():
        nodes = csv_rows(node_path)
        edges = csv_rows(edge_path)
        valid_nodes = [row for row in nodes if re.fullmatch(r"N\d+", (row.get("node_id") or "").strip())]
        valid_edges = [row for row in edges if re.fullmatch(r"E\d+", (row.get("edge_id") or "").strip())]
        node_ids = {row["node_id"].strip() for row in valid_nodes}
        refs = {row.get("from_node", "").strip() for row in valid_edges} | {row.get("to_node", "").strip() for row in valid_edges}
        missing = sorted(ref for ref in refs if ref not in node_ids)
        report["domain_checks"].append({"check": "drainage_graph", "status": "error" if missing else "warning" if len(valid_nodes) != len(nodes) or len(valid_edges) != len(edges) else "ok", "valid_nodes": len(valid_nodes), "ignored_node_rows": len(nodes) - len(valid_nodes), "valid_edges": len(valid_edges), "ignored_edge_rows": len(edges) - len(valid_edges), "missing_node_references": missing})

    rainfall_path = DATA_ROOT / "04_rainfall" / "synthetic_nowcast_3h.csv"
    if rainfall_path.exists():
        rows = csv_rows(rainfall_path)
        missing = sum(not (row.get("forecast_mm_15min") or "").strip() for row in rows)
        report["domain_checks"].append({"check": "rainfall_nowcast", "status": "error" if missing else "ok", "rows": len(rows), "missing_forecast_values": missing, "zones": sorted({row.get("zone_id", "") for row in rows})})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="also fail on warnings")
    args = parser.parse_args()
    report: dict[str, Any] = {"generated_at": datetime.now(timezone.utc).isoformat(), "data_root": DATA_ROOT.relative_to(ROOT).as_posix(), "pilot_bbox": {"south": BBOX[0], "north": BBOX[1], "west": BBOX[2], "east": BBOX[3]}, "files": [], "domain_checks": []}
    if not DATA_ROOT.exists():
        report["files"].append({"status": "error", "error": f"Missing data root: {DATA_ROOT}"})
    else:
        for path in sorted(DATA_ROOT.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() == ".csv":
                report["files"].append(validate_csv(path))
            elif path.suffix.lower() == ".geojson":
                report["files"].append(validate_geojson(path))
            elif path.suffix.lower() in {".asc", ".tif", ".tiff"}:
                report["files"].append(validate_dem(path))
            else:
                report["files"].append(result(path, "reference", "ok", bytes=path.stat().st_size))
    validate_domain_files(report)
    PROCESSED_ROOT.mkdir(parents=True, exist_ok=True)
    report_path = PROCESSED_ROOT / "validation_report.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    all_items = report["files"] + report["domain_checks"]
    errors = sum(item.get("status") == "error" for item in all_items)
    warnings = sum(item.get("status") == "warning" for item in all_items)
    print(f"Validated {len(report['files'])} files: {errors} errors, {warnings} warnings")
    print(f"Report: {report_path.relative_to(ROOT)}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
