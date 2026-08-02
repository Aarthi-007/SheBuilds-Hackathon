import axios from "axios";
import type { ImpactSimulationRequest, ImpactSimulationReport } from "./types";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1",
});

export async function runImpactSimulation(
  payload: ImpactSimulationRequest
): Promise<ImpactSimulationReport> {
  const { data } = await api.post<ImpactSimulationReport>("/impact-simulation", payload);
  return data;
}
