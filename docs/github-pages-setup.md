# GitHub Pages + Local B### 3. Configure Frontend for Production

1. **Create production API configuration**:
   ```typescript
   // In frontend/src/services/api.ts, use environment-based URL
   const API_BASE_URL = import.meta.env.PROD 
     ? 'http://192.168.0.53:8000/api/v1'  // Your actual IP address
     : 'http://localhost:8000/api/v1';
   ```nfiguration

This guide shows how to deploy the frontend to GitHub Pages while running the backend locally.

## Setup Steps

### 1. Configure Your Local Backend for GitHub Pages

1. **Update your `.env` file** (create from `.env.example` if it doesn't exist):
   ```bash
   # Navigate to backend directory first
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env` to add your GitHub Pages URL**:
   ```bash
   # Add your GitHub Pages URL to CORS_ORIGINS
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174,https://pepperumo.github.io
   
   # Make sure API is accessible from outside
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

### 2. Configure Frontend for Production

1. **Create production API configuration**:
   ```typescript
   // In frontend/src/services/api.ts, use environment-based URL
   const API_BASE_URL = import.meta.env.PROD 
     ? 'http://YOUR_LOCAL_IP:8000/api/v1'  // Replace with your actual IP
     : 'http://localhost:8000/api/v1';
   ```

2. **Find your local IP address**:
   ```bash
   # Windows
   ipconfig | findstr IPv4
   
   # Mac/Linux  
   ip addr show | grep inet
   ```
   **Your IP address**: `192.168.0.53` (already found for you!)

### 3. Deploy Frontend to GitHub Pages

1. **Enable GitHub Pages** in your repository:
   - Go to Settings → Pages
   - Source: GitHub Actions

2. **The GitHub Actions workflow will**:
   - Build your React app
   - Deploy to GitHub Pages
   - Make it available at `https://pepperumo.github.io/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines`

### 4. Run Backend Locally

```bash
# Start your backend (make sure .env has the GitHub Pages URL in CORS_ORIGINS)
cd backend
python main.py
```

### 5. Access Your App

- **Frontend**: `https://pepperumo.github.io/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines`
- **Backend**: `http://192.168.0.53:8000`

## Important Considerations

### Security & Access
- **Your backend will be accessible from the internet** on your local IP
- Consider using a VPN or ngrok for secure tunneling
- Be aware of firewall settings

### Network Requirements
- Your computer must be online when users access the GitHub Pages site
- Users need to access your local IP address
- Consider network restrictions (corporate firewalls, etc.)

### Alternative: ngrok Tunnel
For better security and reliability:

```bash
# Install ngrok
# Start your backend first
python backend/main.py

# In another terminal, create tunnel
ngrok http 8000

# Use the ngrok URL (e.g., https://abc123.ngrok.io) in your frontend
```

## Troubleshooting

### CORS Errors
- Make sure your GitHub Pages URL is in `CORS_ORIGINS`
- Check browser console for specific CORS errors

### Connection Issues
- Verify your local IP is accessible from outside
- Check firewall settings
- Try using ngrok for tunneling

### Build Issues
- Make sure all environment variables are set correctly
- Check that the API URL points to your accessible backend