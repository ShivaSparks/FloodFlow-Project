"""Create clean, reproducible Stage 1 outputs without modifying source data."""

from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
from pathlib import Path

import geopandas as gpd
import rasterio

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "flood_project_data"
OUTPUT = ROOT / "data" / "processed"


def clean_drainage_csv(source: Path, target: Path, id_column: str, pattern: str) -> dict[str, int]:
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    valid = [row for row in rows if re.fullmatch(pattern, (row.get(id_column) or "").strip())]
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(valid)
    return {"source_rows": len(rows), "clean_rows": len(valid), "removed_rows": len(rows) - len(valid)}


def normalize_geojson(source: Path, target: Path) -> None:
    frame = gpd.read_file(source)
    if frame.crs is None:
        frame = frame.set_crs("EPSG:4326", allow_override=True)
    frame.to_crs("EPSG:4326").to_file(target, driver="GeoJSON")


def normalize_raster(source: Path, target: Path) -> None:
    with rasterio.open(source) as src:
        profile = src.profile.copy()
        profile.update(driver="GTiff", compress="deflate")
        target.parent.mkdir(parents=True, exist_ok=True)
        with rasterio.open(target, "w", **profile) as dst:
            dst.write(src.read())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="replace the existing processed directory")
    args = parser.parse_args()
    if args.clean and OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True, exist_ok=True)
    summary: dict[str, object] = {"source_root": str(SOURCE), "output_root": str(OUTPUT), "files": [], "drainage": {}}

    nodes = SOURCE / "02_drainage_network" / "drainage_nodes_SYNTHETIC.csv"
    edges = SOURCE / "02_drainage_network" / "drainage_edges_SYNTHETIC.csv"
    if nodes.exists():
        summary["drainage"]["nodes"] = clean_drainage_csv(nodes, OUTPUT / "02_drainage_network" / "drainage_nodes_SYNTHETIC.clean.csv", "node_id", r"N\d+")
    if edges.exists():
        summary["drainage"]["edges"] = clean_drainage_csv(edges, OUTPUT / "02_drainage_network" / "drainage_edges_SYNTHETIC.clean.csv", "edge_id", r"E\d+")

    for source in SOURCE.rglob("*"):
        if not source.is_file():
            continue
        relative = source.relative_to(SOURCE)
        target = OUTPUT / relative
        if source.suffix.lower() == ".geojson":
            target.parent.mkdir(parents=True, exist_ok=True)
            normalize_geojson(source, target)
            summary["files"].append({"source": relative.as_posix(), "output": target.relative_to(ROOT).as_posix(), "type": "normalized_geojson"})
        elif source.suffix.lower() in {".asc", ".tif", ".tiff"}:
            target = target.with_suffix(".tif")
            normalize_raster(source, target)
            summary["files"].append({"source": relative.as_posix(), "output": target.relative_to(ROOT).as_posix(), "type": "normalized_raster"})
        elif source.suffix.lower() == ".csv" and "drainage_" not in source.name:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            summary["files"].append({"source": relative.as_posix(), "output": target.relative_to(ROOT).as_posix(), "type": "csv_copy"})
        elif source.suffix.lower() in {".md", ".py"}:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)

    summary_path = OUTPUT / "preparation_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Prepared processed data under {OUTPUT.relative_to(ROOT)}")
    print(f"Summary: {summary_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
