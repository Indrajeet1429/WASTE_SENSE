import { Route, Routes } from "react-router-dom";
import ProtectedRoute from "./components/common/ProtectedRoute";
import AppLayout from "./components/common/AppLayout";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Machines from "./pages/Machines";
import MachineDetails from "./pages/MachineDetails";
import Trends from "./pages/Trends";
import Alerts from "./pages/Alerts";
import WasteEvents from "./pages/WasteEvents";
import WasteDetails from "./pages/WasteDetails";
import Replay from "./pages/Replay";
import Optimization from "./pages/Optimization";
import Savings from "./pages/Savings";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route path="/login" element={<Login mode="login" />} />
      <Route path="/signup" element={<Login mode="signup" />} />
      <Route element={<ProtectedRoute />}>
        <Route element={<AppLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/machines" element={<Machines />} />
          <Route path="/machines/:id" element={<MachineDetails />} />
          <Route path="/trends" element={<Trends />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/waste-events" element={<WasteEvents />} />
          <Route path="/waste-events/:id" element={<WasteDetails />} />
          <Route path="/replay" element={<Replay />} />
          <Route path="/replay/:id" element={<Replay />} />
          <Route path="/optimization" element={<Optimization />} />
          <Route path="/savings" element={<Savings />} />
        </Route>
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
