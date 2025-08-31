# ChatGPT Augmenter ver 1.0 RELEASE

A web application that provides semantic search capabilities over your ChatGPT conversation history using machine learning embeddings.


## CONTEXT

Hi my name is Ayush Pai, a senior at UNC Chapel Hill. I love being efficiently lazy and self-sufficient when if comes to work, because it gives me more leisure time to speedrun Minecraft (actually jk for that because my ability to use hot keys is slow as molasses). I actually really like ChatGPT but sometimes I feel like I always rely on it. I feel like many of the answers to my questions are which I may have asked similarily in the past. That is what this app is for! It allows you to take your ChatGPT history (which you can export as a json on the official website) and use it to be a basis in which you can ask similar questions to which the application will provide ChatGPT assistant answers to historical similar questions which match your query. Hope you enjoy!


## Progression of this Project

There are 6 core branches/versions for this project: ver0.0, ver0.2, ver0.4, ver0.6, ver0.8, and ver1.0. The other branches are there for convinience for myself if I want to create another version for this project. Here is a brief overview on the surface level of what these versions accomplish.

- **ver0.0**: The root node of the project (also known as master).
- **ver0.2**: Introduced react frontend and backend, but exported data was manually uploaded in local filesytem.
- **ver0.4**: Same as ver0.2 on the surface, but vastly cleaner documentation, decoupling, and formatting of code.
- **ver0.6**: Introduced uploading data on the frontend interface.
- **ver0.8**: Introduced database integration, delete data feature, and multi-user interactibility.
- **ver1.0**: React frontend built as static files for cleaner packaging and dockerfile for deployement.


## Version 1.0 Features

**Core Features:**
- **Semantic Search**: Search through your ChatGPT conversations using advanced sentence transformers
- **Modern Web Interface**: Clean, responsive React-based user interface with enhanced UI/UX
- **Smart Recommendations**: Get relevant conversation snippets based on your search queries
- **Real-time Results**: Intuitive semantic search with similarity scoring

**🆕 New in Version 1.0:**
- **� Enhanced Docker Support**: New optimized Dockerfile with multi-stage builds and CPU-only PyTorch
- **� Static File Integration**: React frontend compiled into static files served directly by Flask
- **� Simplified Deployment**: Single-container deployment with integrated frontend and backend
- **⚡ Streamlined Setup**: Unified `setupApp.py` and `runApp.py` scripts for simplified management
- **🔧 Production Ready**: Optimized Docker container under 2GB for efficient deployment

## System Requirements

- Python 3.11 or higher
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

   *Note: If PostgreSQL is not available, the application will automatically fall back to JSON file storage on your local filesystem.*

   **Video Alternative Instructions:**
   - **Windows**: https://www.youtube.com/watch?v=GpqJzWCcQXY
   - **macOS**: https://www.youtube.com/watch?v=PShGF_udSpk
   - **Linux (Ubuntu)**: https://www.youtube.com/watch?v=tducLYZzElo

3. **Environment Configuration**

    **Backend Database Configuration (Again optional depending if you want to use a database):**
    - Go to the backend database directory:
       ```bash
       cd backend/database
       ```
    - Copy the example environment file and configure your database connection:
       ```bash
       cp .env.example .env
       ```
    - Edit `backend/database/.env` with your PostgreSQL credentials:
       ```properties
       # backend/database/.env
       DB_HOST=localhost
       DB_PORT=5432
       DB_NAME=chatgpt_augmenter
       DB_USER=your_postgres_username
       DB_PASSWORD=your_postgres_password
       ```
    - If using default PostgreSQL installation, `DB_USER` is typically `postgres`.
    - Make sure the database name matches `DB_NAME` (e.g., `chatgpt_augmenter`).
    - Set `DB_PASSWORD` to what you configured during PostgreSQL installation.

    *Note: The application will automatically detect these settings and fall back to JSON storage if the database connection fails.*

4. **Prepare Your Data**
   - Go to ChatGPT and export your data (Settings > Data Export)
   - Extract the `conversations.json` file from your exported data
   - You can now upload `conversations.json` directly through the web interface

5. **Run Initial App Setup**
   ```bash
   python setupApp.py
   ```
   This will:
   - Install Python dependencies (including PostgreSQL drivers)
   - Download and setup the Sentence Transformer model (~80MB)
   - Process your conversations and create embeddings


### Daily Usage

For subsequent runs after the initial setup:

**Start Backend Server**
   ```bash
   python runApp.py
   ```


The app server will run on `http://localhost:8080` 

### Docker Deployment (Alternative Setup)

For containerized deployment, you can use the provided Dockerfile:

1. **Build the Docker Image**
   ```bash
   docker build -t chatgpt-augmenter .
   ```

2. **Run the Container**
   ```bash
   docker run -p 8080:8080 chatgpt-augmenter
   ```

3. **Access the Application**
   - The application will be available at `http://localhost:8080`
   - Upload your `conversations.json` file through the web interface
   - The container includes all dependencies and the ML model

**Docker Features:**
- **Optimized size**: Multi-stage build with CPU-only PyTorch (~2GB total)
- **All-in-one**: Includes backend, frontend, and all dependencies
- **Persistent data**: Use volumes to persist uploaded data and embeddings
- **Production ready**: Configured for deployment environments

**Volume mounting for persistent data:**
```bash
docker run -p 8080:8080 -v $(pwd)/data:/app/backend/data chatgpt-augmenter
```

## How to Use


1. **Start the Application**
   - Run `python runApp.py` to start the backend server

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
├── setupApp.py          # Unified setup script (replaces setupBackend.py/setupFrontend.py)
├── runApp.py            # Unified run script (replaces runBackend.py/runFrontend.py)
├── Dockerfile           # Optimized multi-stage Docker build
├── .dockerignore        # Docker build exclusions
├── .gitignore          # Git exclusions
├── backend/             # Flask API server with integrated static files
│   ├── __init__.py      # Python package initialization
│   ├── app.py           # Main Flask application with static file serving
│   ├── requirements.txt # Python dependencies
│   ├── setup.py         # Backend-specific setup utilities
│   ├── run_flask.py     # Direct Flask server runner
│   ├── load.py          # Data loading utilities
│   ├── delete.py        # Data deletion utilities
│   ├── static/          # Compiled React frontend (ver1.0 feature)
│   │   ├── css/         # Compiled CSS files
│   │   └── js/          # Compiled JavaScript files
│   ├── templates/       # Flask HTML templates
│   │   └── index.html   # Main application template
│   ├── data/            # Application data storage
│   │   └── dummy.txt    # Placeholder file
│   ├── database/        # Database configuration and models
│   │   ├── __init__.py  # Database package initialization
│   │   └── postgres.py  # PostgreSQL connection and operations
│   ├── pythonFiles/     # Core utility scripts
│   │   ├── createVenv.py    # Virtual environment creation
│   │   └── preload.py       # Model initialization and preloading
│   ├── routes/          # API endpoints (modular route structure)
│   │   ├── __init__.py      # Routes package initialization
│   │   ├── extract.py       # Data extraction endpoints
│   │   ├── search.py        # Semantic search operations
│   │   ├── health.py        # Health check endpoint
│   │   └── delete.py        # Data deletion endpoints
│   └── tests/           # Backend unit tests
│       ├── __init__.py      # Test package initialization
│       ├── conftest.py      # Test configuration
│       ├── README.md        # Test documentation
│       ├── requirements-test.txt # Test dependencies
│       ├── test_extract.py  # Extract functionality tests
│       ├── test_search.py   # Search functionality tests
│       ├── test_delete.py   # Delete functionality tests
│       └── test_postgres.py # Database integration tests
```

## Troubleshooting

- **React app not starting**: Make sure Node.js and npm are installed, and run `npm install` in the `react-app` directory
- **Server errors**: Check that the Flask server is running on `http://localhost:8080`
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
- **Environment file missing**: Copy `backend/database/.env.example` to `backend/database/.env` and configure
- **Delete functionality not working**: Ensure proper database permissions and check server logs
- **Storage fallback**: If seeing "JSON fallback" messages, PostgreSQL connection failed but app continues with file storage

## Technical Details

- **Backend**: Flask with sentence-transformers for semantic search
- **Database**: PostgreSQL for production with automatic JSON file fallback
- **Frontend**: Static JS built from React.JS framwork
- **ML Model**: Uses sentence-transformers for creating and comparing text embeddings
- **Storage**: 
  - **Primary**: PostgreSQL with indexed embeddings for fast similarity search
  - **Fallback**: JSON file storage when database is unavailable
  - **Hybrid**: Automatic detection and switching between storage methods
- **API**: RESTful API with CORS support and enhanced data management endpoints
- **Data Management**: Upload, process, search, and delete operations with real-time feedback
- **Performance**: Optimized for large conversation datasets with efficient similarity queries




## Support

Make sure to run `python setupApp.py` for first-time setup and `python runApp.py` for subsequent starts. The application serves both frontend and backend on `http://localhost:8080`. The Sentence Transformer model requires an internet connection for the initial download.

### Version 1.0 Notes
- **Single-port deployment** simplifies access and configuration
- **Docker-first approach** for easy deployment and scaling
- **Static file serving** eliminates need for separate React development server
- **Unified setup scripts** reduce complexity and potential configuration issues
- **Production optimization** with efficient container builds and resource usage

For issues specific to v1.0 features, ensure Docker is properly installed for containerized deployment, or use the Python scripts for local development. The integrated static files mean you only need to access `http://localhost:8080` for the complete application.