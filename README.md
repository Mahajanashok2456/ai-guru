# Mahabharata & Ramayana Chat Application

A full-stack chat application that provides wisdom and guidance from the ancient Indian epics using AI and vector search.

## 🚀 Quick Start

### 1. Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Configure environment variables in .env file
# Make sure ATLAS_URI and GEMINI_API_KEY are set correctly

# Start the FastAPI backend
python main.py
```

Backend will run on: `http://localhost:8000`

### 2. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

Frontend will run on: `http://localhost:3000`

### 3. Test the Backend

```bash
# Run the backend test script to verify everything works
python test_backend.py
```

## 🔧 Configuration

### Environment Variables (.env)

```env
# MongoDB Atlas connection string
ATLAS_URI=your_mongodb_atlas_connection_string_here

# Google Gemini API key
GEMINI_API_KEY=your_gemini_api_key_here
```

### Backend Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `POST /chat` - Main chat endpoint

### Chat Request Format

The backend expects JSON in this exact format:

```json
{
  "question": "What is the Mahabharata about?"
}
```

### Gemini Model Configuration

The backend is configured to use the `gemini-1.5-flash` model for AI responses. Make sure your Gemini API key has access to this model.

## 🐛 Troubleshooting

### 422 Unprocessable Entity Error

If you get a 422 error:

1. **Check the browser console** (F12) for detailed error messages
2. **Verify the backend is running** on port 8000
3. **Check the request format** - must be `{"question": "your text"}`
4. **Ensure proper headers** - `Content-Type: application/json`

### Common Issues

1. **Backend not starting**: Check MongoDB and Gemini API credentials in `.env`
2. **CORS errors**: Make sure the frontend is running on `localhost:3000`
3. **Network errors**: Ensure both backend (8000) and frontend (3000) ports are available

## 📁 Project Structure

```
├── main.py              # FastAPI backend
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── .gitignore          # Git ignore rules
├── test_backend.py     # Backend testing script
├── frontend/           # React frontend
│   ├── src/
│   │   ├── App.js     # Main React component
│   │   ├── index.js   # React entry point
│   │   └── index.css  # Styling
│   ├── package.json   # Node.js dependencies
│   └── index.html     # HTML template
└── README.md          # This file
```

## 🎯 Features

- ✅ Intent classification (factual, guidance, general)
- ✅ Vector search on MongoDB with embeddings
- ✅ AI-powered responses using Google Gemini
- ✅ Modern React UI with real-time chat
- ✅ CORS support for frontend-backend communication
- ✅ Comprehensive error handling and logging
- ✅ Health checks and debugging tools

## 🧪 Testing

Run the backend test script to verify everything is working:

```bash
python test_backend.py
```

This will test:
- Health endpoint connectivity
- Chat endpoint with correct JSON format
- Error handling with incorrect formats

## 📝 Usage

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Type questions about Mahabharata or Ramayana
4. Get AI-powered responses with source evidence
5. View intent classification and wisdom guidance

## 🔍 Debugging

- **Browser Console**: Check F12 for detailed request/response logs
- **Backend Logs**: Check terminal output for server errors
- **Test Script**: Run `python test_backend.py` to verify backend functionality
- **Health Check**: Visit `http://localhost:8000/health` to check backend status