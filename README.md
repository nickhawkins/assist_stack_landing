# Assist Stack - Chrome Extension + FastAPI Backend

This project provides a Chrome extension and FastAPI backend to collect fully rendered HTML from web pages and convert it to Markdown using AI, bypassing Cloudflare issues.

## 🚀 Quick Start

### 1. Backend Setup

Navigate to the backend directory and start the server:

```bash
cd backend
chmod +x start_server.sh
./start_server.sh
```

This will:
- Install Python dependencies automatically
- Start the FastAPI server on `http://localhost:5001`
- Show API documentation at `http://localhost:5001/docs`

**Optional**: Set your OpenAI API key for AI-powered HTML to Markdown conversion:
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

### 2. Chrome Extension Setup

1. Open Chrome and navigate to `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked" and select the `/extension/` directory
4. The "Assist Stack HTML Collector" extension will appear in your toolbar

### 3. Usage

1. Navigate to any web page you want to convert to Markdown
2. Click the "Assist Stack" extension icon
3. Enter a display name for the page
4. Click "Collect HTML"
5. The extension will:
   - Scroll the page to trigger lazy-loaded content
   - Add a base href tag if missing
   - Collect the complete HTML with doctype
   - Send it to the backend for AI processing

## 📁 Project Structure

```
/extension/              # Chrome Extension
├── manifest.json       # Extension manifest with permissions
├── content.js          # Content script for HTML collection
├── popup.js            # Popup script for user interaction
└── popup.html          # Extension popup UI

/backend/               # FastAPI Backend
├── main.py            # FastAPI application with endpoints
├── models.py          # Pydantic models for requests/responses
├── requirements.txt   # Python dependencies
├── start_server.sh    # Server startup script
└── services/
    ├── ai_service.py      # AI service for HTML to Markdown conversion
    ├── job_db.py         # Job database management
    └── background_tasks.py # Background task processing

test_page.html          # Test page for extension functionality
README.md              # This file
```

## 🔧 Features

### Chrome Extension
- **Cloudflare Bypass**: Collects rendered HTML client-side instead of server-side fetching
- **Lazy Loading Support**: Automatically scrolls pages to trigger lazy-loaded content
- **Base URL Handling**: Adds base href tags for proper relative link resolution
- **User-Friendly UI**: Clean popup interface with progress feedback
- **Error Handling**: Comprehensive error messages for troubleshooting

### FastAPI Backend
- **HTML Processing Endpoint**: `/files/create_html` accepts HTML directly from extension
- **Fallback URL Endpoint**: `/files/create_url` for backward compatibility
- **AI Integration**: Converts HTML to clean Markdown using OpenAI GPT-4
- **Job Management**: Tracks processing status with SQLite database
- **Background Processing**: Async task processing for better performance
- **CORS Support**: Configured for Chrome extension access
- **Health Monitoring**: Health check and status endpoints

## 📡 API Endpoints

### POST `/files/create_html`
Accept HTML content directly from the Chrome extension.

**Request:**
```json
{
  "display_name": "Page Title",
  "url": "https://example.com",
  "html": "<!DOCTYPE html><html>...</html>",
  "category": "optional"
}
```

**Response:**
```json
{
  "job_id": "uuid",
  "status": "pending",
  "message": "HTML content received and queued for processing"
}
```

### POST `/files/create_url`
Fallback endpoint that fetches URLs with Playwright (when HTML not provided).

**Request:**
```json
{
  "display_name": "Page Title", 
  "url": "https://example.com",
  "category": "optional"
}
```

### GET `/jobs/{job_id}`
Get the status and result of a specific job.

**Response:**
```json
{
  "job_id": "uuid",
  "status": "completed",
  "display_name": "Page Title",
  "url": "https://example.com",
  "result": "# Converted Markdown Content\n\n..."
}
```

### GET `/jobs`
List recent jobs (up to 100).

### GET `/health`
Health check endpoint.

## 🧪 Testing

A test page is included at `test_page.html` to verify extension functionality:

1. Start the backend server
2. Open `test_page.html` in Chrome
3. Use the extension to collect HTML from the test page
4. Verify that lazy-loaded and dynamic content is captured

The test page includes:
- Content below the fold to test scrolling
- Dynamic content added via JavaScript
- Clear instructions for testing

## ⚙️ Configuration

### Environment Variables

- `OPENAI_API_KEY` - Required for AI content processing
  - Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
  - Without this key, the system will work but won't convert HTML to Markdown

### Chrome Extension Permissions

The extension requires these permissions (defined in `manifest.json`):
- `activeTab` - Access to the current active tab
- `scripting` - Execute content scripts
- `<all_urls>` - Access to all websites

## 🔍 How It Works

1. **User clicks extension** → Popup opens with current page title pre-filled
2. **User enters display name** → Click "Collect HTML" button
3. **Content script activates** → Scrolls page 3 times with 1-second delays
4. **HTML collection** → Captures full HTML with doctype and adds base href
5. **Data transmission** → Sends `{display_name, url, html}` to backend
6. **Background processing** → FastAPI queues job and processes HTML with AI
7. **Result storage** → Converted Markdown stored in database with job status

## 🚨 Error Handling

### Extension
- **No backend connection**: Clear error message with server check instructions
- **Invalid input**: Form validation with helpful feedback
- **Collection failures**: Graceful handling of page access issues

### Backend  
- **Missing HTML**: Returns 400 error "No HTML supplied"
- **Missing fields**: Validates required fields with specific error messages
- **AI failures**: Graceful fallback with informative placeholder content
- **Job tracking**: All failures logged with error details in job database

## 🛠️ Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
python main.py
```

### Testing API Endpoints
```bash
# Test health endpoint
curl http://localhost:5001/health

# Test HTML processing
curl -X POST http://localhost:5001/files/create_html \
  -H "Content-Type: application/json" \
  -d '{"display_name": "Test", "url": "https://example.com", "html": "<!DOCTYPE html><html><body>Test</body></html>"}'
```

### Extension Development
- Make changes to files in `/extension/`
- Go to `chrome://extensions/`
- Click the reload button for the extension
- Test on any webpage

## 📝 License

This project is provided as-is for development and testing purposes.