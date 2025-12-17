import { Component } from "react";
import PropTypes from "prop-types";
import "./ErrorBoundary.css";

/**
 * Error Boundary component that catches JavaScript errors in child components.
 * Displays a fallback UI instead of crashing the entire app.
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo });
    
    // Log error to console (could send to backend for monitoring)
    console.error(`[ErrorBoundary] ${this.props.name || "Component"} error:`, error);
    console.error("[ErrorBoundary] Component stack:", errorInfo.componentStack);
    
    // Optional: Send to backend for logging
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }
  }

  handleRetry = () => {
    this.setState({ hasError: false, error: null, errorInfo: null });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <div className="error-boundary">
          <div className="error-boundary__icon">⚠️</div>
          <h3 className="error-boundary__title">
            {this.props.title || "Something went wrong"}
          </h3>
          <p className="error-boundary__message">
            {this.props.message || "This section failed to load."}
          </p>
          {this.props.showDetails && this.state.error && (
            <details className="error-boundary__details">
              <summary>Error details</summary>
              <pre>{this.state.error.toString()}</pre>
            </details>
          )}
          {this.props.showRetry && (
            <button className="error-boundary__retry" onClick={this.handleRetry}>
              Try Again
            </button>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

ErrorBoundary.propTypes = {
  children: PropTypes.node.isRequired,
  name: PropTypes.string,
  title: PropTypes.string,
  message: PropTypes.string,
  fallback: PropTypes.node,
  showRetry: PropTypes.bool,
  showDetails: PropTypes.bool,
  onError: PropTypes.func,
};

export default ErrorBoundary;

