# ChatGPT Augmenter React App

This is a React.js conversion of the ChatGPT Augmenter Chrome extension. It provides a web-based interface to monitor text input and search through documents using semantic search capabilities.

## Features

- **Text Input Monitoring**: Real-time text input with character counting
- **Document Search**: Search through your documents using semantic similarity
- **Beautiful UI**: Modern, responsive design with gradient backgrounds and smooth animations
- **Real-time Updates**: See changes as you type with live character counting
- **Search Results Display**: Expandable cards showing search results with similarity scores
- **Markdown Support**: Rich text formatting in search results

## Prerequisites

Before running this app, make sure you have:

1. **Node.js** (version 14 or higher)
2. **npm** or **yarn** package manager
3. **Flask Backend** running on `http://localhost:5000`

## Installation

1. Navigate to the react-app directory:
   ```bash
   cd /home/ayush/ChatGPTAugmenter/react-app
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

## Running the Application

1. **Start the Flask Backend** (in a separate terminal):
   ```bash
   cd /home/ayush/ChatGPTAugmenter/backend
   python app.py
   ```

2. **Start the React App**:
   ```bash
   npm start
   ```

3. Open your browser and navigate to `http://localhost:3000`

## Usage

1. **Text Input**: Type your text in the large textarea. The character count will update in real-time.

2. **Search Documents**: Click the "🔍 Search Documents" button to search through your document collection using the text you've entered.

3. **View Results**: Search results will appear in a modal overlay with:
   - Similarity scores for each result
   - Expandable content cards
   - Markdown formatting support
   - Easy navigation and closing options

4. **Clear Text**: Use the "🗑️ Clear Text" button to clear the input field.

## Key Differences from the Chrome Extension

- **Standalone Web App**: No longer requires Chrome extension installation
- **Direct Text Input**: Instead of monitoring ChatGPT input, you type directly in the app
- **Enhanced UI**: Larger interface with better responsiveness
- **Modal Search Results**: Results display in an overlay instead of popup windows
- **Real-time Character Counting**: Live updates as you type

## API Integration

The app communicates with your Flask backend at `http://localhost:5000/search`. The search endpoint expects:

```json
{
  "query": "your search text",
  "top_k": 6
}
```

## Project Structure

```
react-app/
├── public/
│   ├── index.html
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── InputMonitor.js
│   │   ├── InputMonitor.css
│   │   ├── SearchResults.js
│   │   └── SearchResults.css
│   ├── App.js
│   ├── App.css
│   ├── index.js
│   └── index.css
└── package.json
```

## Customization

You can customize the app by:

- **Modifying Colors**: Update the gradient backgrounds in the CSS files
- **Changing Search Parameters**: Adjust the `top_k` value in the search request
- **Adding Features**: Extend the components with additional functionality
- **Styling**: Modify the CSS files to match your preferred design

## Building for Production

To create a production build:

```bash
npm run build
```

This will create a `build` folder with optimized files ready for deployment.

## Troubleshooting

1. **Search Not Working**: Ensure your Flask backend is running on `http://localhost:5000`
2. **Network Errors**: Check that the Flask server is accessible and CORS is properly configured
3. **Styling Issues**: Clear your browser cache or try a hard refresh (Ctrl+F5)

## Future Enhancements

Potential improvements:
- Add file upload functionality for document management
- Implement user authentication
- Add real-time collaboration features
- Include document preview capabilities
- Add export functionality for search results
