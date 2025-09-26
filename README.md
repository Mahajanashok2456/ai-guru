# AI Guru Multibot

A multimodal chat agent built with Google Gemini AI:

- **Text Q&A**: Google Gemini Pro API
- **Image Analysis**: Google Gemini Pro Vision API
- **Session Management**: Grouped conversation history

Cloud-based AI with API integration for better performance and reliability.

## Features

- **Text Chat**: Powered by Google Gemini Pro for intelligent conversations
- **Image Analysis**: Upload and analyze images with Gemini Pro Vision
- **Session Management**: Conversations grouped by session for better organization
- **Chat History**: View previous conversations organized by sessions
- **Modern UI**: React frontend with clean, responsive design
- **Fast API**: Backend built with FastAPI for high performance

## Prerequisites

- **Python 3.12+**
- **Node.js 18+**
- **Google Gemini API Key** ([Get it here](https://makersuite.google.com/))
- **MySQL Database** (Local or cloud)
- **Git** for version control

## Setup

### Backend (Python/FastAPI)

1. **Navigate to backend/**:

   ```bash
   cd backend
   ```

2. **Create virtual environment**:

   ```bash
   python -m venv venv
   ```

3. **Activate environment**:

   ```bash
   venv\Scripts\activate.bat
   ```

4. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

5. **Configure environment variables**:
   Create `.env` file in backend/ directory:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_password
   DB_NAME=guru_multibot
   ```

### Frontend (React)

1. Navigate to `frontend/`:
   ```
   cd frontend
   ```
2. Install dependencies:
   ```
   npm install
   ```

### Database Setup

1. **Install MySQL** and create database:
   ```sql
   CREATE DATABASE guru_multibot;
   USE guru_multibot;
   CREATE TABLE chat_history (
       id INT AUTO_INCREMENT PRIMARY KEY,
       input_type VARCHAR(50),
       user_input TEXT,
       bot_response TEXT,
       session_id VARCHAR(50),
       timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
   );
   ```

## Running the App

1. **Start Backend**:

   ```bash
   cd backend
   venv\Scripts\activate.bat
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start Frontend**:

   ```bash
   cd frontend
   npm start
   ```

3. **Access Application**:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## API Endpoints

- **POST** `/chat` - Text conversation with Gemini Pro
- **POST** `/image-chat` - Image analysis with Gemini Pro Vision
- **GET** `/chat-history` - Get grouped chat sessions
- **DELETE** `/session/{session_id}` - Delete specific session
- **DELETE** `/chat-history` - Delete all chat history

## Technology Stack

- **Frontend**: React.js, Modern CSS
- **Backend**: FastAPI, Python
- **Database**: MySQL
- **AI Models**: Google Gemini Pro & Pro Vision
- **Authentication**: API Key based

## Usage

### Text Chat

1. Type your message in the input field
2. Press Enter or click Send
3. Get intelligent responses from Gemini Pro

### Image Analysis

1. Click the 📷 button to upload an image
2. Add an optional description or question about the image
3. Click "Send Image" to get AI analysis from Gemini Pro Vision

### Session Management

- Conversations are automatically grouped into sessions
- View previous conversations in the sidebar
- Delete individual sessions or all history
- Start new conversations with the "New Chat" button

## Project Structure

```
GuruMultibot/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   ├── .env                # Environment variables
│   └── venv/               # Virtual environment
├── frontend/
│   ├── src/
│   │   ├── App.js          # Main React component
│   │   └── ...             # Other React files
│   ├── package.json        # Node dependencies
│   └── public/             # Static files
└── README.md               # This file
```

## Cost Estimation

- **Gemini Pro**: $0.0005 per 1K characters (~$5-15/month for moderate usage)
- **Gemini Pro Vision**: $0.0025 per image (~$2-10/month depending on image uploads)
- **Total**: Very cost-effective for personal and small business use

## Troubleshooting

- **API Key Issues**: Verify your Gemini API key is correct and active
- **Database Connection**: Ensure MySQL is running and credentials are correct
- **Image Upload**: Supported formats (JPEG, PNG, GIF, WebP)
- **CORS Errors**: Backend must be running on port 8000 for frontend to connect

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Fork, create PRs. Issues welcome.

## License

MIT
