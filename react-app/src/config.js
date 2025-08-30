// API configuration for different environments
const config = {
  // Use environment variable if available, otherwise fall back to defaults
  API_BASE_URL: process.env.REACT_APP_API_BASE_URL || 
    (process.env.NODE_ENV === 'production' ? 'http://localhost:8080' : 'http://localhost:8080')
};

// Export the configuration
export default config;
  