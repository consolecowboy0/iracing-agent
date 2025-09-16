# 🏁 iRacing AI Agent

A real-time AI race engineer and spotter for iRacing that provides voice-enabled race commentary, strategic advice, and track analysis using OpenAI's Realtime API.

## Features

- **Real-time voice communication** with AI race engineer
- **Snarky, experienced race engineer personality** 
- **OpenAI Realtime API integration** for low-latency audio
- **Conversation history management** with export capabilities
- **Web-based control interface** for managing sessions
- **Offline-first design** - works with or without live OpenAI connection

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key with Realtime API access
- Modern web browser with WebRTC support

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/consolecowboy0/iracing-agent.git
   cd iracing-agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_openai_api_key_here
   ```

4. **Start the server**
   ```bash
   # Option 1: Use the startup script (recommended)
   ./start.sh
   
   # Option 2: Start manually
   python server.py
   
   # Option 3: Use uvicorn with auto-reload for development
   uvicorn server:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Open the web interface**
   Open `browser.html` in your web browser. The server will be running on `http://localhost:8000`.

## Configuration

### Environment Variables

- `OPENAI_API_KEY` - Your OpenAI API key (required for online mode)
- `REALTIME_MODEL` - Model to use (default: `gpt-realtime`)
- `HISTORY_PATH` - Path to conversation history file (default: `history.json`)

### Race Engineer Personality

The AI agent is configured with a snarky, experienced race engineer personality that:
- Provides real-time race commentary and strategic advice
- Calls out track conditions, other drivers, and opportunities  
- Stays supportive but doesn't sugarcoat bad driving
- Uses racing terminology naturally
- Keeps responses brief and direct

Example responses:
- *"Nice line through turn 3... finally."*
- *"Gap to the leader is 2.5 seconds and growing - time to stop admiring the scenery."*
- *"Caution out, this is your chance to make up positions if you don't mess it up."*

## API Endpoints

### Session Management

- `GET /session` - Create new AI session
  - `?online=1` - Use live OpenAI API (requires API key)
  - Default: offline stub session for testing

### Conversation History

- `GET /history` - Retrieve conversation history
- `POST /history` - Add message to history
- `DELETE /history` - Clear conversation history
- `POST /history/rotate` - Rotate large history files

### Export Functions

- `GET /history/as-realtime-items` - Export history as Realtime API events
  - `?last_turns=N` - Number of recent conversation turns to include

## Usage Guide

### Basic Operation

1. **Start the server** and open the web interface
2. **Click "Connect"** to establish WebRTC connection with OpenAI
3. **Grant microphone permissions** when prompted
4. **Start talking** - the AI will respond with voice using server-side voice activity detection

### Advanced Features

#### History Management
- **View conversation history** with the "Get" button
- **Add manual messages** to conversation context
- **Export conversation** to continue sessions with context

#### Offline Development
- Use **offline mode** (default) for development without API costs
- **Test the interface** and conversation flow
- **Switch to online mode** when ready for live AI interaction

#### Session Export/Import
- **Export conversation history** as Realtime API events
- **Send exported context** to new sessions
- **Continue conversations** across different sessions

## Development

### Project Structure

```
iracing-agent/
├── server.py          # FastAPI server with history management
├── ai_agent.py        # Legacy agent code (reference)
├── browser.html       # Web interface for controlling the agent
├── requirements.txt   # Python dependencies
├── history.json       # Conversation history storage
├── start.sh           # Startup script (Unix/Linux/Mac)
├── .env.example       # Example environment variables
└── .env              # Environment variables (create this)
```

### Running in Development

```bash
# Start server with auto-reload
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Or use Python directly
python server.py
```

### Testing

The project includes offline capabilities for testing:

1. **Offline mode**: Default behavior, creates local session stubs
2. **History simulation**: Add test messages via the web interface
3. **Export testing**: Test conversation export/import functionality

## Troubleshooting

### Common Issues

**"Browser not supported" or WebRTC errors**
- Ensure you're using a modern browser (Chrome, Firefox, Safari)
- Check microphone permissions
- Try refreshing the page

**OpenAI API errors**
- Verify your API key has Realtime API access
- Check your OpenAI account billing status
- Ensure the API key is correctly set in `.env`

**Connection timeouts**
- Check your internet connection
- Try increasing timeout values in `server.py`
- Use offline mode for development

**Audio not working**
- Check browser microphone permissions
- Verify audio output device
- Test with different browsers

### Development Tips

- **Use offline mode** during development to avoid API costs
- **Monitor the browser console** for WebRTC and JavaScript errors  
- **Check server logs** for FastAPI and OpenAI API issues
- **Test conversation export/import** to ensure context preservation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (offline and online modes)
5. Submit a pull request

## License

This project is open source. Please check the repository for license details.

## Related Projects

- [OpenAI Realtime API Documentation](https://platform.openai.com/docs/guides/realtime)
- [iRacing SDK](https://github.com/kutu/pyirsdk) - For integrating live telemetry data
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework used

---

**Ready to race? Fire up the agent and let's hit the track! 🏎️**