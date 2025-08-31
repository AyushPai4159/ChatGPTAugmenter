# ChatGPT Augmenter

A React web application that provides semantic search capabilities over your ChatGPT conversation history using machine learning embeddings.

## Features

- **Semantic Search**: Search through your ChatGPT conversations using advanced sentence transformers
- **Modern Web Interface**: Clean, responsive React-based user interface
- **Smart Recommendations**: Get relevant conversation snippets based on your search queries
- **Real-time Results**: Fast semantic search with similarity scoring

## System Requirements

- Python 3.11 or higher
- Node.js and npm (required for React app)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- ~80MB of SSD space for the Sentence Transformer model

## Installation & Setup

### Quick Setup (Python Scripts)

1. **Download the Application**
   ```bash
   git clone https://github.com/AyushPai4159/ChatGPTAugmenter.git
   cd ChatGPTAugmenter
   ```

2. **Prepare Your Data**
   - Go to ChatGPT and export your data (Settings > Data Export)
   - Extract the `conversations.json` file from your exported data
   - Create an `uploadData` directory in the root: `mkdir uploadData`
   - Copy `conversations.json` to the `/uploadData/` directory

3. **Setup Backend (Python & ML)**
   ```bash
   python setupBackend.py
   ```
   This will:
   - Set up Python virtual environment
   - Install Python dependencies
   - Download and setup the Sentence Transformer model (~80MB)
   - Process your conversations and create embeddings

4. **Setup Frontend (React)**
   ```bash
   python setupFrontend.py
   ```
   This will:
   - Install all Node.js dependencies
   - Prepare the React development environment

### Daily Usage

**Option 1: Python Convenience Scripts (Recommended)**
```bash
# Start backend server
python runBackend.py

# In a new terminal, start React app
python runFrontend.py
```

**Option 2: Traditional Method**
```bash
# Start backend server
./run.sh

# In a new terminal, start React app
cd react-app
npm start
```

The backend server will run on `http://localhost:8080` and the React app on `http://localhost:3000`.

## How to Use

1. **Start the Application**
   - Run `python runBackend.py` to start the backend server
   - In a new terminal, run `python runFrontend.py` to start the React app
   - The web app will open at `http://localhost:3000`

2. **Search Your Conversations**
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
├── setupBackend.py    # Backend setup script (Python dependencies, ML model)
├── setupFrontend.py   # Frontend setup script (npm install)
├── runBackend.py      # Start Flask server from root
├── runFrontend.py     # Start React app from root
├── uploadData/        # User data directory
│   └── conversations.json  # (You need to add this)
├── backend/          # Flask API server
│   ├── app.py        # Main Flask application
│   ├── requirements.txt
│   ├── setup.py      # Backend setup automation
│   ├── run_flask.py  # Flask server runner
│   ├── load.py       # Backend data loading script
│   ├── delete.py     # Backend data deletion script
│   ├── data/         # Internal backend data
│   ├── pythonFiles/  # Data processing scripts
│   ├── routes/       # API endpoints
│   └── database/     # Database utilities
└── react-app/        # React web application
    ├── package.json  # Node.js dependencies
    ├── public/       # Static assets
    ├── src/          # React source code
    │   ├── App.js    # Main React component
    │   ├── components/ # UI components
    │   └── ...       # Other React files
```

## Troubleshooting

- **React app not starting**: Make sure Node.js and npm are installed, and run `python setupFrontend.py`
- **No search results**: Ensure `conversations.json` is in the `uploadData/` directory and `python setupBackend.py` ran successfully
- **Server errors**: Check that the Flask server is running on `http://localhost:8080` using `python runBackend.py`
- **CORS issues**: The backend is configured to allow requests from `http://localhost:3000`
- **Model download issues**: The setup script will download ~80MB for the Sentence Transformer model
- **Permission errors**: Make sure you have write permissions in the project directory
- **Python environment issues**: The setup scripts automatically handle virtual environment creation

## Common Commands

**Setup (First Time)**
```bash
python setupBackend.py    # Setup Python backend
python setupFrontend.py   # Setup React frontend
```

**Daily Usage**
```bash
python runBackend.py      # Start Flask server
python runFrontend.py     # Start React app (in new terminal)
```

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

**Quick Start**: Run `python setupBackend.py` and `python setupFrontend.py` for first-time setup, then use `python runBackend.py` and `python runFrontend.py` for daily usage.

**Data Location**: Place your `conversations.json` file in the `uploadData/` directory in the root of the project.

**Requirements**: The Sentence Transformer model requires an internet connection for the initial download (~80MB).