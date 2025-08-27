# External Device Access Guide

## The Problem
GitHub Pages serves content over HTTPS, but your backend runs on HTTP. Modern browsers block HTTP requests from HTTPS pages (Mixed Content Security Policy).

## Solutions

### Solution 1: Allow Mixed Content (Recommended for Testing)
1. **Chrome**: Click the shield icon in the address bar → "Load unsafe scripts"
2. **Firefox**: Click the shield icon → "Disable protection for now"
3. **Edge**: Click the shield icon → "Allow unsafe content"

### Solution 2: Access via HTTP Proxy
Instead of accessing `https://pepperumo.github.io/...`, use:
```
http://pepperumo.github.io/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines/
```
(Note: This may not work as GitHub forces HTTPS)

### Solution 3: Local Network Access
1. Make sure both devices are on the same WiFi network
2. On the computer running the backend, find your IP: `192.168.0.53`
3. On the other device, access: `http://192.168.0.53:8000` to test backend
4. If that works, then the GitHub Pages site should work with mixed content allowed

### Solution 4: Enable HTTPS on Backend (Advanced)
Would require SSL certificate setup on your backend server.

## Current Configuration
- **Backend IP**: `192.168.0.53:8000`
- **Frontend detects**: Environment correctly configured
- **Issue**: HTTPS → HTTP mixed content blocked

## Testing Steps
1. **First**: Test if backend is reachable from other device:
   - Open browser on other device
   - Go to: `http://192.168.0.53:8000/health`
   - Should show: `{"status":"healthy",...}`

2. **Second**: If backend is reachable, allow mixed content:
   - Go to GitHub Pages site: `https://pepperumo.github.io/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines/`
   - When you see "Connection Error", look for shield/lock icon in address bar
   - Click it and allow "unsafe scripts" or "mixed content"
   - Retry the connection

3. **Third**: Site should now load with backend data