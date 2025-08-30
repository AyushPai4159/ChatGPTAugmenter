import React, { useState } from 'react';
import axios from 'axios';
import './FileUpload.css';

const FileUpload = ({ userUUID }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    
    if (file) {
      // Check if file is JSON
      if (file.type !== 'application/json' && !file.name.endsWith('.json')) {
        setUploadStatus('error');
        alert('Please select a JSON file');
        return;
      }
      
      // Check if filename is conversations.json
      if (file.name !== 'conversations.json') {
        setUploadStatus('error');
        alert('File must be named "conversations.json"');
        return;
      }
      
      setSelectedFile(file);
      setUploadStatus('');
    }
  };

  const integrateBackendUpload = async () => {
    try {
      console.log("Sending upload request to backend with UUID:", userUUID);
      console.log("File:", selectedFile?.name);
      
      // Read the JSON file content
      const fileContent = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const jsonData = JSON.parse(e.target.result);
            resolve(jsonData);
          } catch (parseError) {
            reject(new Error('Invalid JSON file format'));
          }
        };
        reader.onerror = () => reject(new Error('Failed to read file'));
        reader.readAsText(selectedFile);
      });
      
      // Prepare the payload
      const payload = {
        uuid: userUUID,
        data: fileContent
      };
      
      console.log("Sending payload to /extract endpoint...");
      
      // Send to backend
      const response = await axios.post('/extract', payload, {
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      console.log("Backend response:", response.data);
      setIsUploading(false);
      setUploadStatus('success');
      
    } catch (error) {
      console.error("Upload error:", error);
      setIsUploading(false);
      setUploadStatus('error');
      
      // Show specific error message
      if (error.response?.data?.error) {
        alert(`Upload failed: ${error.response.data.error}`);
      } else if (error.message) {
        alert(`Upload failed: ${error.message}`);
      } else {
        alert('Upload failed. Please try again.');
      }
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Please select a conversations.json file first');
      return;
    }

    setIsUploading(true);
    setUploadStatus('uploading');
    integrateBackendUpload()
    
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadStatus('');
    // Reset the file input
    const fileInput = document.getElementById('file-input');
    if (fileInput) {
      fileInput.value = '';
    }
  };

  return (
    <div className="file-upload">
      <div className="upload-container">
        <div className="upload-header">
          <h3>📁 Upload Conversations Data</h3>
          <p className="upload-description">
            Upload your exported ChatGPT conversations.json file to enable semantic search
          </p>
        </div>

        <div className="upload-section">
          <div className="file-input-container">
            <input
              id="file-input"
              type="file"
              accept=".json,application/json"
              onChange={handleFileSelect}
              className="file-input"
              disabled={isUploading}
            />
            <label htmlFor="file-input" className="file-input-label">
              {selectedFile ? selectedFile.name : 'Choose conversations.json file'}
            </label>
          </div>

          {selectedFile && (
            <div className="file-info">
              <div className="file-details">
                <span className="file-name">📄 {selectedFile.name}</span>
                <span className="file-size">
                  ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
            </div>
          )}

          <div className="upload-buttons">
            <button
              onClick={handleUpload}
              disabled={!selectedFile || isUploading}
              className={`upload-btn ${uploadStatus}`}
            >
              {isUploading ? '⏳ Processing...' : '🚀 Upload & Process'}
            </button>

            {selectedFile && (
              <button
                onClick={resetUpload}
                disabled={isUploading}
                className="reset-btn"
              >
                🗑️ Clear
              </button>
            )}
          </div>

          {uploadStatus && (
            <div className={`upload-status ${uploadStatus}`}>
              {uploadStatus === 'uploading' && '⏳ Uploading and processing your conversations...'}
              {uploadStatus === 'success' && '✅ Upload completed successfully!'}
              {uploadStatus === 'error' && '❌ Upload failed. Please try again.'}
            </div>
          )}
        </div>

        <div className="upload-help">
          <h4>How to get your conversations.json file:</h4>
          <ol>
            <li>Go to ChatGPT and log in to your account</li>
            <li>Go to Settings → Data Export</li>
            <li>Request your data export</li>
            <li>Download and extract the file named "conversations.json"</li>
            <li>Upload that file here</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
