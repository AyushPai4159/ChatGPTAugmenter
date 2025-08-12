# ChatGPT Augmenter

A React web application that provides semantic search capabilities over your ChatGPT conversation history using machine learning embeddings.

## Version 0.8 Features

- **Semantic Search**: Search through your ChatGPT conversations using advanced sentence transformers
- **Modern Web Interface**: Clean, responsive React-based user interface with enhanced UX
- **Smart Recommendations**: Get relevant conversation snippets based on your search queries
- **Real-time Results**: Fast semantic search with similarity scoring
- **🗑️ Delete Functionality**: New delete button to remove uploaded data after processing
- **🗄️ PostgreSQL Integration**: Robust database storage with automatic JSON file fallback
- **🔄 Hybrid Storage**: Seamless switching between PostgreSQL and JSON storage based on availability
- **📊 Data Management**: Enhanced data upload, processing, and deletion capabilities

## System Requirements

- Python 3.10 or higher
- Node.js and npm (required for React app)
- PostgreSQL 12+ (recommended) or fallback to JSON file storage
- Modern web browser (Chrome, Firefox, Safari, Edge)
- ~80MB of SSD space for the Sentence Transformer model
- Additional storage for conversation embeddings (varies by data size)

## Installation & Setup

### First Time Setup

1. **Download the Application**
   ```bash
   git clone https://github.com/AyushPai4159/ChatGPTAugmenter.git
   cd ChatGPTAugmenter
   ```

2. **Database Setup (Recommended but not Mandatory given JSON Filesystem Backup)**
   
   **Install PostgreSQL for your platform:**
   - **macOS**: https://www.postgresql.org/download/macosx/
   - **Windows**: https://www.postgresql.org/download/windows/
   - **Linux (Ubuntu)**: https://www.postgresql.org/download/linux/ubuntu/
   - **Linux (Other)**: https://www.postgresql.org/download/linux/
   
   
   
   **After installation, create the database:**
   ```bash
   # Create database (works on all platforms after PostgreSQL installation)
   createdb chatgpt_augmenter
   
   # Alternative using psql console:
   psql -U postgres
   CREATE DATABASE chatgpt_augmenter;
   \q
   ```
   
   *Note: If PostgreSQL is not available, the application will automatically fall back to JSON file storage on your local filesytem.*


   **Video Alternative Instructions:**
   - **Windows**: https://www.youtube.com/watch?app=desktop&vx=GpqJzWCcQXY
   - **macOS**: https://www.youtube.com/watch?v=PShGF_udSpk
   - **Linux (Ubuntu)**: https://www.youtube.com/watch?v=tducLYZzElo

3. **Environment Configuration**
   
   **Frontend Environment Setup:**
   ```bash
   cd react-app
   ```
   Create or verify the `.env` file with the correct backend URL:
   ```properties
   # react-app/.env
   REACT_APP_API_BASE_URL=http://localhost:5001
   ```
   
   **Backend Database Configuration:**
   ```bash
   cd backend/database
   ```
   Copy the example environment file and configure your database connection:
   ```bash
   # Copy the example file
   cp .env.example .env
   ```
   
   Edit `backend/database/.env` with your PostgreSQL credentials:
   ```properties
   # backend/database/.env
   DB_HOST=localhost
   DB_PORT=5432
   DB_NAME=chatgpt_augmenter
   DB_USER=your_postgres_username
   DB_PASSWORD=your_postgres_password
   ```
   
   **Default Database Settings:**
   - If using default PostgreSQL installation, `DB_USER` is typically `postgres`
   - Create the database name to match `DB_NAME` (e.g., `chatgpt_augmenter`)
   - Set `DB_PASSWORD` to what you configured during PostgreSQL installation
   
   *Note: The application will automatically detect these settings and fall back to JSON storage if the database connection fails.*

4. **Prepare Your Data**
   - Go to ChatGPT and export your data (Settings > Data Export)
   - Extract the `conversations.json` file from your exported data
   - Copy `conversations.json` to the `/backend/data/` directory

5. **Run Initial Setup**
   ```bash
   sh backend.sh
   ```
   This will:
   - Install Python dependencies (including PostgreSQL drivers)
   - Download and setup the Sentence Transformer model (~80MB)
   - Configure database connection (PostgreSQL or JSON fallback)
   - Process your conversations and create embeddings
   - Start the Flask backend server

6. **Setup React Web Application**
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

The backend server will run on `http://localhost:5001` and the React app on `http://localhost:3000`.

## How to Use

1. **Start the Application**
   - Run `./run.sh` to start the backend server
   - Navigate to the `react-app` directory and run `npm start`
   - The web app will open at `http://localhost:3000`

2. **Upload and Manage Your Data**
   - Use the file upload interface to add your `conversations.json` file
   - The system will automatically process and store data in PostgreSQL (or JSON fallback)
   - **New in v0.8**: Use the delete button (🗑️) to remove uploaded data when needed
   - Monitor upload progress and processing status in real-time

3. **Search Your Conversations**
   - Enter your search query in the input field
   - Click the "Search Documents" button
   - View relevant conversation snippets with similarity scores
   - Browse through the results to find relevant information from your ChatGPT history

4. **Data Management Features**
   - **Delete uploaded data**: Click the delete button to remove processed conversations
   - **Database status**: View current storage method (PostgreSQL vs JSON fallback)
   - **Processing status**: Monitor embedding generation and data processing
   - **Storage efficiency**: PostgreSQL provides faster queries for large datasets

5. **Monitor Input (Simulation Feature)**
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
│   ├── requirements.txt # Python dependencies (includes psycopg2)
│   ├── database/      # Database configuration and models
│   │   ├── postgres.py # PostgreSQL connection and operations
│   │   ├── .env       # Database credentials (create from .env.example)
│   │   └── .env.example # Template for database configuration
│   ├── data/          # Your conversation data
│   │   └── conversations.json  # (You need to add this)
│   ├── pythonFiles/   # Data processing scripts
│   │   ├── sentenceTransform.py # ML embeddings
│   │   └── preload.py # Database initialization
│   └── routes/        # API endpoints
│       ├── extract.py # Data extraction with delete functionality
│       └── search.py  # Semantic search operations
├── react-app/         # React web application (main app)
│   ├── package.json   # Node.js dependencies
│   ├── .env          # Frontend environment (API URL configuration)
│   ├── public/        # Static assets
│   ├── src/           # React source code
│   │   ├── App.js     # Main React component
│   │   ├── components/ # UI components
│   │   │   ├── FileUpload.js # Enhanced upload with delete
│   │   │   └── SearchResults.js # Results display
│   │   └── ...        # Other React files
│   └── README.md      # React-specific documentation
└── frontend/          # Legacy browser extension (deprecated)
```

## Troubleshooting

- **React app not starting**: Make sure Node.js and npm are installed, and run `npm install` in the `react-app` directory
- **No search results**: Ensure `conversations.json` is in the correct location and `startup.sh` ran successfully
- **Server errors**: Check that the Flask server is running on `http://localhost:5001`
- **CORS issues**: The backend is configured to allow requests from `http://localhost:3000`
- **Model download issues**: The setup script will download ~80MB for the Sentence Transformer model
- **Database connection issues**: 
  - **macOS**: Check PostgreSQL service: `brew services list | grep postgresql`
  - **Windows**: Check service in Services.msc or Task Manager → Services tab → Look for "postgresql"
  - **Linux**: Check service: `sudo systemctl status postgresql`
  - If PostgreSQL fails, the app will automatically use JSON file fallback
  - **macOS/Linux**: Verify database exists: `psql -l | grep chatgpt_augmenter`
  - **Windows**: Use pgAdmin or Command Prompt: `psql -U postgres -l`
  - **Environment Configuration**: Ensure `backend/database/.env` has correct credentials
  - **Connection Test**: Check that database name matches between `.env` and actual database
- **Frontend connection issues**: 
  - Verify `react-app/.env` has correct `REACT_APP_API_BASE_URL=http://localhost:5001`
  - Ensure backend is running on the same port specified in the React environment file
- **Environment file missing**: Copy `backend/database/.env.example` to `backend/database/.env` and configure
- **Delete functionality not working**: Ensure proper database permissions and check server logs
- **Storage fallback**: If seeing "JSON fallback" messages, PostgreSQL connection failed but app continues with file storage

## Technical Details

- **Backend**: Flask with sentence-transformers for semantic search
- **Database**: PostgreSQL for production with automatic JSON file fallback
- **Frontend**: React web application with modern UI components and enhanced UX
- **ML Model**: Uses sentence-transformers for creating and comparing text embeddings
- **Storage**: 
  - **Primary**: PostgreSQL with indexed embeddings for fast similarity search
  - **Fallback**: JSON file storage when database is unavailable
  - **Hybrid**: Automatic detection and switching between storage methods
- **API**: RESTful API with CORS support and enhanced data management endpoints
- **Data Management**: Upload, process, search, and delete operations with real-time feedback
- **Performance**: Optimized for large conversation datasets with efficient similarity queries

## Version 0.8 New Features

### 🗑️ Delete Functionality
- **One-click deletion**: Remove uploaded conversation data with a single button click
- **Complete cleanup**: Removes both raw data and processed embeddings
- **Confirmation dialogs**: Prevents accidental data loss
- **Real-time feedback**: Progress indicators during deletion process

### 🗄️ Database Integration
- **PostgreSQL primary storage**: Fast, reliable database for conversation embeddings
- **Automatic fallback**: Seamless switch to JSON files if database is unavailable
- **Connection resilience**: Handles database disconnections gracefully
- **Migration support**: Easy transition from JSON to PostgreSQL storage

### 📊 Enhanced Data Management
- **Upload progress tracking**: Real-time feedback during file processing
- **Storage method display**: Shows whether using PostgreSQL or JSON fallback
- **Error handling**: Comprehensive error messages and recovery suggestions
- **Performance monitoring**: Query timing and optimization metrics

## Development

To modify or extend the application:

1. **Backend changes**: Edit files in `/backend/` 
2. **React app changes**: Edit files in `/react-app/src/`
3. **Adding new components**: Create new files in `/react-app/src/components/`
4. **Styling**: Modify CSS files in `/react-app/src/`
5. **Database operations**: Modify `/backend/database/postgres.py` for PostgreSQL features
6. **API endpoints**: Add new routes in `/backend/routes/` directory
7. **Data processing**: Enhance `/backend/pythonFiles/` for improved ML operations

### Development Environment Setup

**Unix/macOS/Linux:**
```bash
# Backend development
cd backend
pip install -r requirements.txt
flask run --debug

# Frontend development  
cd react-app
npm install
npm start

# Database development
createdb chatgpt_augmenter_dev
psql chatgpt_augmenter_dev
```

**Windows:**
```powershell
# Backend development
cd backend
pip install -r requirements.txt
set FLASK_ENV=development
flask run --debug

# Frontend development  
cd react-app
npm install
npm start

# Database development (Command Prompt as Administrator)
createdb chatgpt_augmenter_dev
psql -U postgres chatgpt_augmenter_dev

# Alternative using psql directly
psql -U postgres
CREATE DATABASE chatgpt_augmenter_dev;
\c chatgpt_augmenter_dev
```

## Support

Make sure to run `startup.sh` for first-time setup and `run.sh` for subsequent backend starts. Don't forget to run `npm start` in the `react-app` directory to launch the web application. The Sentence Transformer model requires an internet connection for the initial download.

### Version 0.8 Notes
- **PostgreSQL recommended** for better performance with large datasets
- **JSON fallback ensures functionality** even without database setup
- **Delete feature requires confirmation** to prevent accidental data loss
- **Hybrid storage system** provides maximum reliability and flexibility
- **Enhanced error handling** provides better user feedback and troubleshooting guidance

For issues specific to v0.8 features, check the database connection status and ensure proper file permissions for both PostgreSQL and JSON fallback storage.