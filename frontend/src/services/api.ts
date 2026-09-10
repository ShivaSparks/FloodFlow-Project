import axios from "axios";

export type RiskLevel = "safe" | "watch" | "dangerous" | "blocked";

export type AuthUser = { id: number; name: string; email: string; role: "PUBLIC" | "ADMIN" | string; avatar_url?: string | null };

export type Prediction = {
  road_id: string;
  predicted_depth_cm: number;
  risk_level: RiskLevel;
  final_risk_level?: RiskLevel;
  ml_flood_probability?: number;
  drainage_utilization: number;
  confidence: number;
};

export type ForecastStep = {
  simulation_time_minutes: number;
  rainfall_mm_15min?: number;
  cumulative_rainfall_mm?: number;
  predictions: Prediction[];
  data_mode: string;
  is_simulation: boolean;
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api",
  withCredentials: true,
  timeout: 5000,
});

const fallbackStep = (lead: number): ForecastStep => ({
  simulation_time_minutes: lead,
  rainfall_mm_15min: lead === 0 ? 8 : Math.max(2, 14 - lead / 18),
  cumulative_rainfall_mm: 8 + lead * 0.45,
  data_mode: "synthetic",
  is_simulation: true,
  predictions: [
    { road_id: "SR001", predicted_depth_cm: lead * 0.8, risk_level: lead > 60 ? "dangerous" : "watch", drainage_utilization: Math.min(1.3, 0.3 + lead / 120), confidence: 0.63 },
    { road_id: "SR002", predicted_depth_cm: lead * 0.6, risk_level: lead > 90 ? "dangerous" : "watch", drainage_utilization: Math.min(1.2, 0.28 + lead / 150), confidence: 0.63 },
    { road_id: "SR003", predicted_depth_cm: lead * 1.6, risk_level: lead > 30 ? "dangerous" : "watch", drainage_utilization: Math.min(1.5, 0.35 + lead / 100), confidence: 0.63 },
  ],
});

export async function fetchTimeline(): Promise<ForecastStep[]> {
  try {
    const response = await api.get<{ steps: ForecastStep[] }>("/flood/timeline");
    return response.data.steps;
  } catch {
    return [0, 15, 30, 60, 120, 165].map(fallbackStep);
  }
}

export async function fetchHealth(): Promise<boolean> {
  try {
    await api.get("/../health");
    return true;
  } catch {
    return false;
  }
}

export async function requestSafeRoute(payload: {
  start_latitude: number;
  start_longitude: number;
  end_latitude: number;
  end_longitude: number;
  transport: string;
  forecast_lead_minutes?: number;
}) {
  const response = await api.post("/routes/safe", payload, { timeout: 20000 });
  return response.data;
}

export async function searchAddress(query: string) {
  const response = await api.get<Array<{ display_name: string; lat: string; lon: string; result_type?: string }>>("/routes/geocode", { params: { q: query }, timeout: 10000 });
  return response.data;
}

export async function fetchReports() {
  const response = await api.get<ReportTicket[]>("/reports/flood");
  return response.data;
}

export type ReportTicket = { id: number; latitude: number | null; longitude: number | null; water_depth_category: string; road_status: string; verification_status: string; status: string; admin_note?: string | null; photo_url?: string | null; confidence: number | null; observed_at: string; user_id?: number | null };
export async function fetchMyReports() { const response = await api.get<ReportTicket[]>("/reports/mine"); return response.data; }
export async function fetchAdminReports() { const response = await api.get<ReportTicket[]>("/admin/reports"); return response.data; }
export async function updateReportStatus(id: number, status: string, admin_note?: string) { const response = await api.patch(`/admin/reports/${id}`, { status, admin_note }); return response.data; }
export async function deleteReport(id: number) { await api.delete(`/admin/reports/${id}`); }
export async function submitFloodReport(payload: { latitude: number; longitude: number; water_depth_category: string; road_status: string; comment?: string; photo_url?: string | null; observed_at: string }) {
  const response = await api.post("/reports/flood", payload);
  return response.data;
}

export async function simulatorAction(action: "start" | "pause" | "reset" | "advance") {
  const response = await api.post(`/simulator/${action}`);
  return response.data;
}

export async function fetchSimulatorStatus() {
  const response = await api.get("/simulator/status");
  return response.data;
}

export async function login(email: string, password: string) { const response = await api.post("/auth/login", { email, password }); return response.data; }
export async function logout() { await api.post("/auth/logout"); }
export async function getCurrentUser(): Promise<AuthUser> { const response = await api.get<AuthUser>("/auth/me"); return response.data; }
export async function register(name: string, email: string, password: string): Promise<AuthUser> { const response = await api.post<AuthUser>("/auth/register", { name, email, password }); return response.data; }
export async function updateProfile(payload: { name: string; avatar_url?: string | null }): Promise<AuthUser> { const response = await api.patch<AuthUser>("/auth/me", payload); return response.data; }
