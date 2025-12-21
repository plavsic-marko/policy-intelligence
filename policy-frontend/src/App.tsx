import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import History from "./pages/History";
import PolicyChat from "./pages/PolicyChat";


function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<PolicyChat />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
