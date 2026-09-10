import { create } from "zustand";
import { fetchTimeline, type ForecastStep } from "../services/api";

type FloodStore = {
  steps: ForecastStep[];
  selectedLead: number;
  loading: boolean;
  apiOnline: boolean;
  loadTimeline: () => Promise<void>;
  setSelectedLead: (lead: number) => void;
};

export const useFloodStore = create<FloodStore>((set) => ({
  steps: [],
  selectedLead: 60,
  loading: false,
  apiOnline: false,
  loadTimeline: async () => {
    set({ loading: true });
    const steps = await fetchTimeline();
    set({ steps, loading: false, apiOnline: steps.length > 0 });
  },
  setSelectedLead: (selectedLead) => set({ selectedLead }),
}));
