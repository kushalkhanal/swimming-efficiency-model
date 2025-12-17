import { Routes, Route } from "react-router-dom";
import DashboardPage from "./pages/DashboardPage";
import Layout from "./components/Layout";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<DashboardPage />} />
      </Routes>
    </Layout>
  );
}

export default App;

