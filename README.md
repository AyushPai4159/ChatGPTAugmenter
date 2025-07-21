# ChatGPT Augmenter

A browser extension that enhances ChatGPT by providing semantic search capabilities over your conversation history using machine learning embeddings.

## Features

- **Semantic Search**: Search through your ChatGPT conversations using advanced sentence transformers
- **Real-time Integration**: Seamlessly integrates with ChatGPT interface
- **Smart Recommendations**: Get relevant conversation snippets based on your current prompt
- **Cross-browser Support**: Works with Chrome and Firefox

## System Requirements

- Python 3.7 or higher
- Node.js and npm (if using React version)
- Chrome or Firefox browser with developer extensions enabled
- ~80MB of SSD space for the Sentence Transformer model

## Installation & Setup

### First Time Setup

1. **Download the Application**
   ```bash
   git clone https://github.com/AyushPai4159/ChatGPTAugmenter.git
   cd ChatGPTAugmenter
   ```

2. **Prepare Your Data**
   - Go to ChatGPT and export your data (Settings > Data Export)
   - Extract the `conversations.json` file from your exported data
   - Copy `conversations.json` to the `/backend/data/` directory

3. **Run Initial Setup**
   ```bash
   ./startup.sh
   ```
   This will:
   - Install Python dependencies
   - Download and setup the Sentence Transformer model (~80MB)
   - Process your conversations and create embeddings
   - Start the Flask backend server

4. **Install Browser Extension**
   - Open Chrome or Firefox
   - Go to Extensions/Add-ons page
   - Enable "Developer mode" 
   - Click "Load unpacked extension" (Chrome) or "Load Temporary Add-on" (Firefox)
   - Select the `/frontend/` directory from this project

### Daily Usage

For subsequent runs after the initial setup:

```bash
./run.sh
```

This will start the backend server without re-downloading the model or re-processing data.

## How to Use

1. **Start the Application**
   - Run `./run.sh` to start the backend server
   - The extension should be loaded in your browser

2. **Use with ChatGPT**
   - Go to ChatGPT (chat.openai.com)
   - Start typing a prompt in the input field
   - The extension will automatically extract and analyze your input

3. **Search Your Conversations**
   - Click on the ChatGPT Augmenter extension icon in your browser
   - Click the "Search Documents" button
   - View relevant conversation snippets that match your current context
   - Use these results to inform or enhance your ChatGPT prompts

## Project Structure

```
ChatGPTAugmenter/
├── README.md
├── startup.sh          # First-time setup script
├── run.sh             # Daily startup script
├── backend/           # Flask API server
│   ├── app.py         # Main Flask application
│   ├── requirements.txt
│   ├── data/          # Your conversation data
│   │   └── conversations.json  # (You need to add this)
│   └── pythonFiles/   # Data processing scripts
├── frontend/          # Browser extension
│   ├── manifest.json  # Extension configuration
│   ├── popup.html     # Extension popup interface
│   ├── popup.js       # Extension popup logic
│   └── content.js     # ChatGPT page integration
└── react-app/         # React web version (optional)
```

## Troubleshooting

- **Extension not loading**: Make sure developer mode is enabled in your browser
- **No search results**: Ensure `conversations.json` is in the correct location and `startup.sh` ran successfully
- **Server errors**: Check that the Flask server is running on `http://localhost:5000`
- **Model download issues**: The setup script will download ~80MB for the Sentence Transformer model

## Technical Details

- **Backend**: Flask with sentence-transformers for semantic search
- **Frontend**: Vanilla JavaScript browser extension with React version available
- **ML Model**: Uses sentence-transformers for creating and comparing text embeddings
- **Storage**: Processes conversations into vector embeddings for fast similarity search

## Development

To modify or extend the application:

1. Backend changes: Edit files in `/backend/` 
2. Extension changes: Edit files in `/frontend/`
3. React version: Use the `/react-app/` directory

## Support

Make sure to run `startup.sh` for first-time setup and `run.sh` for subsequent uses. The Sentence Transformer model requires an internet connection for the initial download.