import { Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import ComparisonPage from "./pages/ComparisonPage";
import Layout from "./components/Layout";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/compare" element={<ComparisonPage />} />
      </Routes>
    </Layout>
  );
}

export default App;

