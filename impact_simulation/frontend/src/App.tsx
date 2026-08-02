import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import ImpactSimulation from "./routes/ImpactSimulation";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/impact-simulation" replace />} />
        <Route path="/impact-simulation" element={<ImpactSimulation />} />
      </Routes>
    </BrowserRouter>
  );
}
