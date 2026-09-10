import { useEffect, useRef, useState } from "react";
import maplibregl, { type Map } from "maplibre-gl";
import type { Prediction } from "../services/api";

const pilotBoundary = {
  type: "Feature" as const,
  properties: {},
  geometry: {
    type: "Polygon" as const,
    coordinates: [[[80.18, 12.9], [80.245, 12.9], [80.245, 13.0], [80.18, 13.0], [80.18, 12.9]]],
  },
};

const hotspots = [
  { name: "Velachery commercial belt", coordinates: [80.2181, 12.9815] },
  { name: "Pallikaranai marsh edge", coordinates: [80.199, 12.937] },
  { name: "Echankadu Signal", coordinates: [80.201, 12.944] },
];

type Props = { predictions?: Prediction[]; onRoadSelect?: (roadId: string) => void; routeGeometry?: { type: "LineString"; coordinates: number[][] } | null; routePoints?: { start?: [number, number]; destination?: [number, number] }; onRoutePointChange?: (point: "start" | "destination", coordinates: [number, number]) => void; onMapClick?: (coordinates: [number, number]) => void };

const riskColor = ["match", ["get", "risk"], "blocked", "#ef4444", "dangerous", "#fb7185", "watch", "#f59e0b", "#34d399"] as any;

function circlePolygon(longitude: number, latitude: number, radius: number) {
  return Array.from({ length: 25 }, (_, index) => {
    const angle = (index / 24) * Math.PI * 2;
    return [longitude + Math.cos(angle) * radius, latitude + Math.sin(angle) * radius * 0.7];
  });
}

const rainfallParticles = Array.from({ length: 22 }, (_, index) => ({ longitude: 80.18 + ((index * 0.017) % 0.064), latitude: 12.905 + ((index * 0.031) % 0.09) }));

export default function MapView({ predictions = [], onRoadSelect, routeGeometry = null, routePoints, onRoutePointChange, onMapClick }: Props) {
  const container = useRef<HTMLDivElement>(null);
  const map = useRef<Map | null>(null);
  const [roadFeatures, setRoadFeatures] = useState<any[]>([]);
  const [mapReady, setMapReady] = useState(false);
  const [routeScreenPoints, setRouteScreenPoints] = useState("");
  const routeMarkers = useRef<{ start?: maplibregl.Marker; destination?: maplibregl.Marker }>({});

  useEffect(() => { void fetch("/data/osm_aligned_roads.geojson").then((response) => response.json()).then((data) => setRoadFeatures(data.features ?? [])).catch(() => setRoadFeatures([])); }, []);

  useEffect(() => {
    if (!container.current || map.current) return;
    const instance = new maplibregl.Map({
      container: container.current,
      center: [80.215, 12.95],
      zoom: 11.4,
      style: {
        version: 8,
        sources: {
          osm: {
            type: "raster",
            tiles: ["https://tile.openstreetmap.org/{z}/{x}/{y}.png"],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors",
          },
        },
        layers: [{ id: "osm", type: "raster", source: "osm" }],
      },
    });
    instance.addControl(new maplibregl.NavigationControl(), "top-right");
    let particleTimer: number | undefined;
    let waterTimer: number | undefined;
    instance.on("load", () => {
      instance.addSource("pilot-boundary", { type: "geojson", data: pilotBoundary });
      instance.addLayer({
        id: "pilot-boundary",
        type: "line",
        source: "pilot-boundary",
        paint: { "line-color": "#19c3b1", "line-width": 2, "line-dasharray": [3, 2] },
      });
      instance.addSource("flood-water", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      instance.addLayer({ id: "flood-water", type: "fill", source: "flood-water", paint: { "fill-color": "#38bdf8", "fill-opacity": 0.24 } });
      instance.addLayer({ id: "flood-water-outline", type: "line", source: "flood-water", paint: { "line-color": "#7dd3fc", "line-width": 2, "line-opacity": 0.75 } });
      instance.addSource("rain-particles", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      instance.addLayer({ id: "rain-particles", type: "circle", source: "rain-particles", paint: { "circle-color": "#bfdbfe", "circle-radius": 2, "circle-opacity": 0.72 } });
      instance.addSource("drainage-flow", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      instance.addLayer({ id: "drainage-flow", type: "symbol", source: "drainage-flow", layout: { "text-field": "➜", "text-size": 18, "text-allow-overlap": true, "text-rotate": 25 }, paint: { "text-color": "#38bdf8", "text-halo-color": "#082f49", "text-halo-width": 1 } });
      instance.addSource("safe-route", { type: "geojson", data: { type: "FeatureCollection", features: [] } });
      instance.addLayer({ id: "safe-route-glow", type: "line", source: "safe-route", layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": "#60a5fa", "line-width": 14, "line-opacity": 0.38, "line-blur": 2 } });
      instance.addLayer({ id: "safe-route", type: "line", source: "safe-route", layout: { "line-cap": "round", "line-join": "round" }, paint: { "line-color": "#0057ff", "line-width": 7, "line-opacity": 1 } });
      let particleStep = 0;
      particleTimer = window.setInterval(() => {
        const particleSource = instance.getSource("rain-particles") as maplibregl.GeoJSONSource | undefined;
        if (!particleSource) return;
        particleStep = (particleStep + 1) % 40;
        particleSource.setData({ type: "FeatureCollection", features: rainfallParticles.map((particle, index) => ({ type: "Feature", properties: {}, geometry: { type: "Point", coordinates: [particle.longitude, particle.latitude - ((particleStep + index * 3) % 40) * 0.00045] } })) });
      }, 120);
      let waterPulse = 0;
      waterTimer = window.setInterval(() => { waterPulse += 0.35; if (instance.getLayer("flood-water")) instance.setPaintProperty("flood-water", "fill-opacity", 0.18 + Math.abs(Math.sin(waterPulse)) * 0.13); }, 180);
      instance.addSource("hotspots", {
        type: "geojson",
        data: {
          type: "FeatureCollection",
          features: hotspots.map((hotspot) => ({
            type: "Feature",
            properties: { name: hotspot.name },
            geometry: { type: "Point", coordinates: hotspot.coordinates },
          })),
        },
      });
      instance.addLayer({
        id: "hotspots",
        type: "circle",
        source: "hotspots",
        paint: {
          "circle-color": "#ff6b5f",
          "circle-radius": 7,
          "circle-stroke-color": "#ffffff",
          "circle-stroke-width": 2,
        },
      });
      instance.addSource("risk-roads", {
        type: "geojson",
        data: { type: "FeatureCollection", features: [] },
      });
      instance.addLayer({
        id: "risk-roads-glow",
        type: "line",
        source: "risk-roads",
        paint: { "line-color": riskColor, "line-width": ["interpolate", ["linear"], ["get", "depth"], 0, 3, 20, 8, 50, 13], "line-opacity": 0.25, "line-blur": 4 },
      });
      instance.addLayer({
        id: "risk-roads",
        type: "line",
        source: "risk-roads",
        paint: { "line-color": riskColor, "line-width": ["interpolate", ["linear"], ["get", "depth"], 0, 2, 20, 5, 50, 8], "line-opacity": 0.9 },
      });
      instance.moveLayer("safe-route-glow");
      instance.moveLayer("safe-route");
      instance.on("click", "risk-roads", (event) => {
        const roadId = event.features?.[0]?.properties?.road_id;
        if (roadId) onRoadSelect?.(String(roadId));
      });
      instance.on("mouseenter", "risk-roads", () => { instance.getCanvas().style.cursor = "pointer"; });
      instance.on("mouseleave", "risk-roads", () => { instance.getCanvas().style.cursor = ""; });
      instance.on("click", (event) => onMapClick?.([event.lngLat.lng, event.lngLat.lat]));
      setMapReady(true);
    });
    map.current = instance;
    return () => {
      if (particleTimer) window.clearInterval(particleTimer);
      if (waterTimer) window.clearInterval(waterTimer);
      routeMarkers.current.start?.remove(); routeMarkers.current.destination?.remove();
      instance.remove();
      map.current = null;
    };
  }, [onRoadSelect, onMapClick]);

  useEffect(() => {
    const instance = map.current;
    if (!mapReady || !instance || !routePoints) return;
    (['start', 'destination'] as const).forEach((point) => {
      const coordinates = routePoints[point];
      if (!coordinates) { routeMarkers.current[point]?.remove(); delete routeMarkers.current[point]; return; }
      const marker = routeMarkers.current[point] ?? new maplibregl.Marker({ color: point === "start" ? "#22c55e" : "#ef4444", draggable: true });
      if (!routeMarkers.current[point]) {
        marker.on("dragend", () => { const lngLat = marker.getLngLat(); onRoutePointChange?.(point, [lngLat.lng, lngLat.lat]); });
        routeMarkers.current[point] = marker;
      }
      marker.setLngLat(coordinates).addTo(instance);
    });
  }, [mapReady, routePoints, onRoutePointChange]);

  useEffect(() => {
    const instance = map.current;
    if (!mapReady || !instance || !instance.isStyleLoaded() || !instance.getSource("risk-roads")) return;
    const source = instance.getSource("risk-roads") as maplibregl.GeoJSONSource;
    source.setData({
      type: "FeatureCollection",
      features: roadFeatures.map((road) => {
        const prediction = predictions.find((item) => item.road_id === road.properties?.road_id);
        return { ...road, properties: { ...road.properties, road_id: road.properties?.road_id, risk: prediction?.final_risk_level ?? prediction?.risk_level ?? "safe", depth: prediction?.predicted_depth_cm ?? 0 } };
      }),
    });
    const maxDepth = Math.max(...predictions.map((prediction) => prediction.predicted_depth_cm), 0);
    const waterSource = instance.getSource("flood-water") as maplibregl.GeoJSONSource | undefined;
    if (waterSource) waterSource.setData({ type: "FeatureCollection", features: hotspots.map((hotspot, index) => ({ type: "Feature", properties: { depth: maxDepth }, geometry: { type: "Polygon", coordinates: [circlePolygon(hotspot.coordinates[0], hotspot.coordinates[1], 0.0018 + Math.min(maxDepth / 500, 0.009) * (1 + index * 0.12))] } })) });
    const flowSource = instance.getSource("drainage-flow") as maplibregl.GeoJSONSource | undefined;
    if (flowSource) flowSource.setData({ type: "FeatureCollection", features: hotspots.map((hotspot, index) => ({ type: "Feature", properties: {}, geometry: { type: "Point", coordinates: [hotspot.coordinates[0] + 0.004 + (maxDepth > 10 ? 0.001 : 0), hotspot.coordinates[1] - index * 0.001] } })) });
  }, [mapReady, predictions, roadFeatures]);

  useEffect(() => {
    const instance = map.current;
    if (!mapReady || !instance || !instance.isStyleLoaded() || !instance.getSource("safe-route")) return;
    const source = instance.getSource("safe-route") as maplibregl.GeoJSONSource;
    const routeData = { type: "FeatureCollection" as const, features: routeGeometry ? [{ type: "Feature" as const, properties: {}, geometry: routeGeometry }] : [] };
    const paintRoute = () => { source.setData(routeData); if (instance.getLayer("safe-route-glow")) instance.moveLayer("safe-route-glow"); if (instance.getLayer("safe-route")) instance.moveLayer("safe-route"); instance.triggerRepaint(); };
    paintRoute();
    window.setTimeout(paintRoute, 250);
    if (routeGeometry?.coordinates.length) {
      const first = routeGeometry.coordinates[0] as [number, number];
      const bounds = routeGeometry.coordinates.reduce((result, coordinate) => result.extend(coordinate as [number, number]), new maplibregl.LngLatBounds(first, first));
      instance.fitBounds(bounds, { padding: 70, maxZoom: 14, duration: 900 });
    }
  }, [mapReady, routeGeometry]);

  useEffect(() => {
    const instance = map.current;
    if (!mapReady || !instance || !routeGeometry?.coordinates.length) { setRouteScreenPoints(""); return; }
    const projectRoute = () => setRouteScreenPoints(routeGeometry.coordinates.map((coordinate) => { const point = instance.project(coordinate as [number, number]); return `${point.x},${point.y}`; }).join(" "));
    projectRoute();
    instance.on("move", projectRoute); instance.on("resize", projectRoute);
    return () => { instance.off("move", projectRoute); instance.off("resize", projectRoute); };
  }, [mapReady, routeGeometry]);

  return <div className="map-shell"><div ref={container} className="map-canvas" aria-label="Interactive Chennai flood map" />{routeScreenPoints && <svg className="route-screen-overlay" aria-hidden="true"><polyline points={routeScreenPoints} /></svg>}</div>;
}
