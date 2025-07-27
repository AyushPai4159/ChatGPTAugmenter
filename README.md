# ChatGPT Augmenter

A React web application that provides semantic search capabilities over your ChatGPT conversation history using machine learning embeddings.

## Features

- **Semantic Search**: Search through your ChatGPT conversations using advanced sentence transformers
- **Modern Web Interface**: Clean, responsive React-based user interface
- **Smart Recommendations**: Get relevant conversation snippets based on your search queries
- **Real-time Results**: Fast semantic search with similarity scoring

## System Requirements

- Python 3.7 or higher
- Node.js and npm (required for React app)
- Modern web browser (Chrome, Firefox, Safari, Edge)
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
   - You can now upload `conversations.json` directly through the web interface

3. **Run Initial Setup**
   ```bash
   ./startup.sh
   ```
   This will:
   - Install Python dependencies
   - Download and setup the Sentence Transformer model (~80MB)
   - Process your conversations and create embeddings
   - Start the Flask backend server

4. **Setup React Web Application**
   ```bash
   cd react-app
   npm install
   npm start
   ```
   This will:
   - Install all Node.js dependencies
   - Start the React development server
   - Open the application in your browser at `http://localhost:3000`

### Daily Usage

For subsequent runs after the initial setup:

1. **Start Backend Server**
   ```bash
   ./run.sh
   ```

2. **Start React Application**
   ```bash
   cd react-app
   npm start
   ```

The backend server will run on `http://localhost:5000` and the React app on `http://localhost:3000`.

## How to Use

1. **Start the Application**
   - Run `./run.sh` to start the backend server
   - Navigate to the `react-app` directory and run `npm start`
   - The web app will open at `http://localhost:3000`

2. **Upload Your Conversations**
   - Click the "Upload Conversations" button in the web interface
   - Select your `conversations.json` file from your ChatGPT data export
   - Wait for the processing to complete (this creates embeddings for search)

3. **Search Your Conversations**
   - Enter your search query in the input field
   - Click the "Search Documents" button
   - View relevant conversation snippets with similarity scores
   - Browse through the results to find relevant information from your ChatGPT history

3. **Monitor Input (Simulation Feature)**
   - The app includes a ChatGPT input simulator
   - Type in the text area to simulate ChatGPT input monitoring
   - Use the "Clear" and "Search" buttons to interact with the interface

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
├── react-app/         # React web application (main app)
│   ├── package.json   # Node.js dependencies
│   ├── public/        # Static assets
│   ├── src/           # React source code
│   │   ├── App.js     # Main React component
│   │   ├── components/ # UI components
│   │   └── ...        # Other React files
│   └── README.md      # React-specific documentation
└── frontend/          # Legacy browser extension (deprecated)
```

## Troubleshooting

- **React app not starting**: Make sure Node.js and npm are installed, and run `npm install` in the `react-app` directory
- **No search results**: Ensure you have uploaded your `conversations.json` file through the web interface and processing completed successfully
- **Server errors**: Check that the Flask server is running on `http://localhost:5000`
- **CORS issues**: The backend is configured to allow requests from `http://localhost:3000`
- **Model download issues**: The setup script will download ~80MB for the Sentence Transformer model

## Technical Details

- **Backend**: Flask with sentence-transformers for semantic search
- **Frontend**: React web application with modern UI components
- **ML Model**: Uses sentence-transformers for creating and comparing text embeddings
- **Storage**: Processes conversations into vector embeddings for fast similarity search
- **API**: RESTful API with CORS support for web app integration

## Development

To modify or extend the application:

1. **Backend changes**: Edit files in `/backend/` 
2. **React app changes**: Edit files in `/react-app/src/`
3. **Adding new components**: Create new files in `/react-app/src/components/`
4. **Styling**: Modify CSS files in `/react-app/src/`

## Support

Make sure to run `startup.sh` for first-time setup and `run.sh` for subsequent backend starts. Don't forget to run `npm start` in the `react-app` directory to launch the web application. The Sentence Transformer model requires an internet connection for the initial download.