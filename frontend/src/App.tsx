import { Routes, Route, Navigate } from "react-router-dom";
import Layout from "@/components/Layout";
import ReportsListPage from "@/pages/ReportsListPage";
import RunsListPage from "@/pages/RunsListPage";
import RunDetailPage from "@/pages/RunDetailPage";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/reports" replace />} />
        <Route path="/reports" element={<ReportsListPage />} />
        <Route path="/reports/:slug/runs" element={<RunsListPage />} />
        <Route path="/runs/:runId" element={<RunDetailPage />} />
      </Route>
    </Routes>
  );
}
