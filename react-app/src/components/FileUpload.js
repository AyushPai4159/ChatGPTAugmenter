import React, { useState } from 'react';
import axios from 'axios';
import config from '../config';
import './FileUpload.css';

const FileUpload = ({ userUUID }) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [enableDelete, setEnableDelete] = useState(false);

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
            reject(new Error('Invalid JSON file format, probably an empty or corrupted file'));
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
      
      // Send to backend with authentication headers
      const response = await axios.post(`${config.API_BASE_URL}/extract`, payload);
      
      console.log("Backend response:", response.data);
      setIsUploading(false);
      setUploadStatus('success');
      setEnableDelete(true); // Enable delete button after successful upload
      
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

  const handleDelete = async () => {
    if (!userUUID) {
      alert('No user UUID available for deletion');
      return;
    }

    // Confirm deletion
    const confirmDelete = window.confirm(
      '⚠️ Are you sure you want to delete all your data from the database? This action cannot be undone.'
    );
    
    if (!confirmDelete) {
      return;
    }

    setIsUploading(true);
    setUploadStatus('deleting');

    try {
      console.log("Sending delete request for UUID:", userUUID);
      
      // Send delete request to backend with authentication headers
      const response = await axios.delete(`${config.API_BASE_URL}/delete/${userUUID}`);
      
      console.log("Delete response:", response.data);
      setIsUploading(false);
      setUploadStatus('deleted');
      setEnableDelete(false); // Disable delete button after successful deletion
      
      // Reset file selection after successful deletion
      setSelectedFile(null);
      const fileInput = document.getElementById('file-input');
      if (fileInput) {
        fileInput.value = '';
      }
      
    } catch (error) {
      console.error("Delete error:", error);
      setIsUploading(false);
      setUploadStatus('delete-error');
      
      // Show specific error message
      if (error.response?.data?.error) {
        alert(`Delete failed: ${error.response.data.error}`);
      } else if (error.message) {
        alert(`Delete failed: ${error.message}`);
      } else {
        alert('Delete failed. Please try again.');
      }
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setUploadStatus('');
    setEnableDelete(false); // Reset delete state
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
                onClick={enableDelete ? handleDelete : resetUpload}
                disabled={isUploading}
                className={enableDelete ? "delete-btn" : "reset-btn"}
              >
                {enableDelete ? '🗑️ Delete Data' : '🗑️ Clear'}
              </button>
            )}
          </div>

          {uploadStatus && (
            <div className={`upload-status ${uploadStatus}`}>
              {uploadStatus === 'uploading' && '⏳ Uploading and processing your conversations...'}
              {uploadStatus === 'success' && '✅ Upload completed successfully!'}
              {uploadStatus === 'error' && '❌ Upload failed. Please try again.'}
              {uploadStatus === 'deleting' && '🗑️ Deleting your data from the database...'}
              {uploadStatus === 'deleted' && '✅ All your data has been successfully deleted!'}
              {uploadStatus === 'delete-error' && '❌ Delete failed. Please try again.'}
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
