# Quick Setup Guide: Local Backend + GitHub Pages Frontend

## ✅ **YES! You can run backend locally and serve frontend from GitHub Pages**

This setup allows you to:
- 🌐 **Frontend**: Deployed on GitHub Pages (free, fast, reliable)
- 🏠 **Backend**: Running on your local machine (with all your data and ML)
- 🔗 **Connection**: Frontend makes API calls to your local backend

## 🚀 Quick Setup (5 minutes)

### Step 1: Configure Backend for GitHub Pages

1. **Create/update your `.env` file**:
   ```bash
   cd backend
   cp .env.example .env
   ```
   ✅ **Note**: Your `.env` file is already configured!

2. **Edit `.env` to add GitHub Pages URL**:
   ```bash
   # Add your GitHub Pages URL to CORS_ORIGINS
   CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:5174,https://pepperumo.github.io
   
   # Ensure backend is accessible
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

### Step 2: Find Your Local IP Address

```bash
# Windows
ipconfig | findstr IPv4

# Mac/Linux
ip addr show | grep inet
```
**✅ Your IP Address**: `192.168.0.53` (already found for you!)

### Step 3: Update Frontend API Configuration

Edit the GitHub Actions workflow file to use your IP:
```yaml
# In .github/workflows/deploy-frontend.yml, line 48
VITE_API_BASE_URL: 'http://192.168.0.53:8000'  # Your actual IP (already configured!)
```

### Step 4: Enable GitHub Pages

1. Go to your repository on GitHub
2. **Settings** → **Pages** 
3. **Source**: GitHub Actions
4. Push changes to trigger deployment

### Step 5: Start Your Backend

```bash
cd backend
python main.py
```

**That's it!** Your app will be available at:
- **Frontend**: `https://pepperumo.github.io/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines`
- **Backend**: `http://192.168.0.53:8000`

## 🔧 Alternative: Using ngrok (Recommended for Security)

If you want a secure tunnel instead of exposing your IP:

1. **Install ngrok**: [ngrok.com](https://ngrok.com)
2. **Start your backend**: `python backend/main.py`
3. **Create tunnel**: `ngrok http 8000`
4. **Use ngrok URL**: Update the GitHub Actions workflow with your ngrok URL (e.g., `https://abc123.ngrok.io`)

## ⚠️ Important Notes

### Security Considerations
- Your backend will be accessible from the internet
- Consider using ngrok for better security
- Be aware of firewall settings

### Network Requirements
- Your computer must be online when users access the site
- Users need to reach your local IP/ngrok URL
- Check corporate firewall restrictions

### CORS Troubleshooting
If you get CORS errors:
1. Make sure GitHub Pages URL is in your `.env` CORS_ORIGINS
2. Check browser console for exact error
3. Verify backend is running and accessible

## 🎯 Benefits of This Setup

✅ **Free hosting** for frontend (GitHub Pages)  
✅ **Full control** over backend and data  
✅ **No deployment complexity** for backend  
✅ **Real-time ML** capabilities maintained  
✅ **Easy updates** - just push to GitHub  

## 📝 Quick Test

1. Start backend: `python backend/main.py`
2. Test locally: `http://localhost:8000/health`
3. Test from outside: `http://192.168.0.53:8000/health`
4. Deploy frontend and test the GitHub Pages URL

You now have a hybrid deployment with the best of both worlds! 🎉