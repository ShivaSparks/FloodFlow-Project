import { useEffect, useMemo, useState } from "react";
import { motion } from "framer-motion";
import { Pause, Play, RefreshCw, SlidersHorizontal } from "lucide-react";
import MapView from "../components/MapView";
import StatCard from "../components/StatCard";
import { useFloodStore } from "../store/useFloodStore";

export default function LiveMap() {
  const { steps, selectedLead, setSelectedLead, loading, loadTimeline } = useFloodStore();
  const [playing, setPlaying] = useState(false);
  const [selectedRoadId, setSelectedRoadId] = useState<string | null>(null);
  const selected = steps.find((step) => step.simulation_time_minutes === selectedLead) ?? steps[0];
  const predictions = selected?.predictions ?? [];
  const roadsAtRisk = predictions.filter((item) => item.final_risk_level !== "safe" && item.risk_level !== "safe").length;
  const maxDepth = predictions.length ? Math.max(...predictions.map((item) => item.predicted_depth_cm)) : 0;
  const maxDrainage = predictions.length ? Math.max(...predictions.map((item) => item.drainage_utilization)) : 0;
  const selectedRoad = useMemo(() => predictions.find((item) => item.road_id === selectedRoadId), [predictions, selectedRoadId]);

  useEffect(() => {
    if (!playing || !steps.length) return;
    const timer = window.setInterval(() => {
      const index = steps.findIndex((step) => step.simulation_time_minutes === selectedLead);
      const next = steps[(index + 1) % steps.length];
      setSelectedLead(next.simulation_time_minutes);
    }, 1400);
    return () => window.clearInterval(timer);
  }, [playing, selectedLead, setSelectedLead, steps]);

  return (
    <section className="dashboard-page">
      <div className="page-heading">
        <div><p className="eyebrow">Chennai monitoring centre</p><h1>Live flood map</h1><p className="muted">Flood forecast for the Velachery–Pallikaranai–Medavakkam pilot area.</p></div>
        <button className="outline-button" onClick={() => void loadTimeline()}><RefreshCw size={16} />{loading ? "Refreshing" : "Refresh"}</button>
      </div>
      <div className="stat-grid">
        <StatCard label="Forecast Horizon" value={`+${selected?.simulation_time_minutes ?? 0} min`} detail="Simulated forecast" tone="blue" />
        <StatCard label="Roads at Risk" value={String(roadsAtRisk)} detail="Pilot area" tone="orange" />
        <StatCard label="Peak Flood Depth" value={`${maxDepth.toFixed(1)} cm`} detail="At selected time" tone="red" />
        <StatCard label="Drainage Load" value={`${maxDrainage.toFixed(1)}×`} detail={`${Math.max(0, Math.round((maxDrainage - 1) * 100))}% above capacity`} tone="green" />
      </div>
      <div className="map-layout">
        <div className="map-panel"><MapView predictions={predictions} onRoadSelect={setSelectedRoadId} /><div className="map-badge"><span className="pulse-dot" /> Simulated flood forecast · Pilot roads</div><div className="map-legend"><strong>Road flood risk</strong><span><i className="legend-line safe" />Safe</span><span><i className="legend-line watch" />Watch</span><span><i className="legend-line dangerous" />Dangerous</span><span><i className="legend-line blocked" />Blocked</span></div><motion.div className="map-live-ripple" animate={{ scale: [1, 1.5, 1], opacity: [0.5, 0, 0.5] }} transition={{ duration: 2.4, repeat: Infinity }} /></div>
        <aside className="control-panel">
          <div className="panel-title"><span><SlidersHorizontal size={17} /> Forecast Timeline</span><small>Next 3 hours</small></div>
          <button className="play-button" onClick={() => setPlaying((value) => !value)}>{playing ? <Pause size={17} fill="currentColor" /> : <Play size={17} fill="currentColor" />} {playing ? "Pause forecast" : "Play forecast"}</button>
          <div className="timeline">
            {(steps.length ? steps : [0, 15, 30, 60, 120, 165].map((simulation_time_minutes) => ({ simulation_time_minutes }))).map((step) => (
              <button key={step.simulation_time_minutes} className={step.simulation_time_minutes === selectedLead ? "time-chip selected" : "time-chip"} onClick={() => setSelectedLead(step.simulation_time_minutes)}>
                <b>{step.simulation_time_minutes === 0 ? "Now" : `+${step.simulation_time_minutes}m`}</b>
              </button>
            ))}
          </div>
          <div className="coverage-note"><strong>Pilot area</strong><p>Detailed flood prediction is available inside the pilot area.</p></div>
          {selectedRoad && <motion.div className="road-detail" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}><small>SELECTED ROAD</small><strong>{selectedRoad.road_id}</strong><span className={`risk-pill ${selectedRoad.final_risk_level ?? selectedRoad.risk_level}`}>{selectedRoad.final_risk_level ?? selectedRoad.risk_level}</span><p>{selectedRoad.predicted_depth_cm.toFixed(1)} cm predicted depth · {Math.round(selectedRoad.drainage_utilization * 100)}% drainage load</p></motion.div>}
        </aside>
      </div>
    </section>
  );
}
