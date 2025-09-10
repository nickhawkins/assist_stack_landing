# Assist Stack - Chrome Extension + FastAPI Backend

This project provides a Chrome extension and FastAPI backend to collect fully rendered HTML from web pages and convert it to Markdown using AI, bypassing Cloudflare issues.

## Components

### Chrome Extension (`/extension/`)

The Chrome extension collects fully rendered HTML from web pages by:
- Scrolling the page to trigger lazy-loaded content
- Adding a base href tag if missing
- Collecting the complete HTML with doctype
- Sending the data to the FastAPI backend

**Files:**
- `manifest.json` - Extension manifest with required permissions
- `content.js` - Content script for HTML collection
- `popup.js` - Popup script for user interaction
- `popup.html` - Extension popup UI

### FastAPI Backend (`/backend/`)

The FastAPI backend processes HTML content and converts it to Markdown using AI.

**Files:**
- `main.py` - FastAPI application with endpoints
- `models.py` - Pydantic models for requests/responses
- `services/ai_service.py` - AI service for HTML to Markdown conversion
- `services/job_db.py` - Job database management
- `services/background_tasks.py` - Background task processing
- `requirements.txt` - Python dependencies

## Setup

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

4. Run the server:
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:5001`

### Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `/extension/` directory
4. The extension will appear in your browser toolbar

## Usage

1. Navigate to any web page you want to convert to Markdown
2. Click the "Assist Stack" extension icon
3. Enter a display name for the page
4. Click "Collect HTML"
5. The extension will scroll the page, collect HTML, and send it to the backend
6. The backend will process the HTML and convert it to Markdown using AI

## API Endpoints

### POST /files/create_html
Accepts HTML content directly from the Chrome extension.

**Request:**
```json
{
  "display_name": "Page Title",
  "url": "https://example.com",
  "html": "<html>...</html>",
  "category": "optional"
}
```

### POST /files/create_url
Fallback endpoint that fetches URLs with Playwright (when HTML not provided).

**Request:**
```json
{
  "display_name": "Page Title", 
  "url": "https://example.com",
  "category": "optional"
}
```

### GET /jobs/{job_id}
Get the status of a specific job.

### GET /jobs
List recent jobs.

### GET /health
Health check endpoint.

## Features

- **Cloudflare Bypass**: Uses Chrome extension to collect rendered HTML instead of server-side fetching
- **Lazy Loading Support**: Scrolls pages to trigger lazy-loaded content
- **Base URL Handling**: Automatically adds base href for relative links
- **AI Processing**: Converts HTML to clean Markdown using OpenAI
- **Job Management**: Tracks processing status with database
- **Error Handling**: Comprehensive error handling and logging
- **CORS Support**: Configured for Chrome extension access

## Environment Variables

- `OPENAI_API_KEY` - Required for AI content processing