import PropTypes from "prop-types";

import "./Layout.css";

function Layout({ children }) {
  return (
    <div className="app-shell">
      <header className="app-header">
        <h1>Offline Swim Analysis</h1>
        <p>Biomechanical insights without the cloud.</p>
      </header>
      <main className="app-content">{children}</main>
    </div>
  );
}

Layout.propTypes = {
  children: PropTypes.node.isRequired
};

export default Layout;

