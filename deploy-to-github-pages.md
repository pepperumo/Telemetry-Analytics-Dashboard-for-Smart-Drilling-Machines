# Deploy Frontend to GitHub Pages

## Manual Deployment Instructions

### Prerequisites
1. **Local Backend Running**: Make sure your backend is running locally on `http://localhost:8000`
2. **CORS Configured**: Backend is already configured to allow GitHub Pages origin

### Step 1: Build Frontend (Already Done)
```bash
cd frontend
npm run build
```

### Step 2: Deploy to GitHub Pages

#### Option A: Using GitHub Web Interface (Recommended)
1. Go to your repository: https://github.com/pepperumo/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines
2. Go to **Settings** → **Pages**
3. Under **Source**, select "Deploy from a branch"
4. Select **dev** branch and **/ (root)** folder
5. Click **Save**

#### Option B: Create gh-pages Branch (Alternative)
```bash
# From project root
cd ..
git checkout --orphan gh-pages
git rm -rf .
cp -r frontend/dist/* .
cp frontend/dist/.* . 2>/dev/null || true
git add .
git commit -m "Deploy to GitHub Pages"
git push origin gh-pages
```

### Step 3: Configure GitHub Pages
1. In your repo, go to **Settings** → **Pages**
2. Under **Source**, select "Deploy from a branch"
3. Select **gh-pages** branch and **/ (root)** folder
4. Click **Save**

### Step 4: Access Your App
Your app will be available at:
```
https://pepperumo.github.io/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines/
```

## How It Works
- **Frontend**: Hosted on GitHub Pages (static files)
- **Backend**: Running locally on your PC at `http://localhost:8000`
- **Communication**: Frontend makes API calls to your local backend
- **CORS**: Configured to allow GitHub Pages origin

## Important Notes

### For the Frontend to Work:
1. **Keep your backend running locally** while using the GitHub Pages version
2. **Your PC must be online** and accessible
3. **Backend port 8000** must be available

### Security Considerations:
- Your backend is only accessible from your local network
- GitHub Pages serves static files only
- No sensitive data is exposed through GitHub Pages

### Updating the Deployment:
1. Make changes to your frontend code
2. Run `npm run build` in the frontend directory
3. Copy new files to gh-pages branch or update via GitHub interface
4. Changes will be live in a few minutes

## Troubleshooting

### Frontend can't connect to backend:
- Ensure backend is running: `curl http://localhost:8000/health`
- Check browser console for CORS errors
- Verify GitHub Pages URL in browser network tab

### GitHub Pages not updating:
- Wait 5-10 minutes for deployment
- Clear browser cache
- Check GitHub Actions tab for deployment status

### CORS Issues:
- Backend already configured for GitHub Pages domain
- If issues persist, check browser developer tools console