# GitHub Pages Deployment Guide

This guide explains how to deploy the frontend to GitHub Pages from the `dev` branch.

## Setup Complete

The project is now configured for automatic GitHub Pages deployment with the following setup:

### 1. Frontend Configuration
- **gh-pages package**: Installed as dev dependency
- **Vite configuration**: Updated `vite.config.prod.ts` with correct base URL
- **Build scripts**: Added production build and deployment scripts

### 2. GitHub Actions Workflow
- **File**: `.github/workflows/deploy-gh-pages.yml`
- **Triggers**: 
  - Push to `dev` branch with changes in `frontend/` folder
  - Manual workflow dispatch
- **Process**: Builds frontend and deploys to `gh-pages` branch

### 3. Backend Setup
- **Scripts available**: `start-backend.bat` (Windows) and `start-backend.sh` (Linux/Mac)
- **Virtual environment**: Already configured in `backend/venv`
- **Dependencies**: Managed via `requirements.txt`

## How to Deploy

### Automatic Deployment
1. Push changes to the `dev` branch
2. GitHub Actions will automatically build and deploy the frontend
3. Your site will be available at: `https://pepperumo.github.io/Telemetry-Analytics-Dashboard-for-Smart-Drilling-Machines/`

### Manual Deployment
From the frontend directory:
```bash
npm run deploy
```

### Running the Backend Locally
Choose your platform:

**Windows:**
```bash
./start-backend.bat
```

**Linux/Mac:**
```bash
./start-backend.sh
```

## GitHub Pages Configuration

After the first deployment, you need to:

1. Go to your repository settings
2. Navigate to "Pages" in the left sidebar
3. Set source to "Deploy from a branch"
4. Select `gh-pages` branch and `/ (root)` folder
5. Save the settings

## Available Scripts

### Frontend
- `npm run dev`: Start development server
- `npm run build`: Regular build
- `npm run build:prod`: Production build for GitHub Pages
- `npm run deploy`: Build and deploy to GitHub Pages
- `npm run preview`: Preview production build

### Backend
- Use the provided `.bat` or `.sh` scripts for easy startup
- The scripts handle virtual environment setup, dependencies, and server startup

## Workflow Details

The GitHub Actions workflow:
1. Triggers on pushes to `dev` branch affecting `frontend/` files
2. Sets up Node.js environment
3. Installs frontend dependencies
4. Builds the application with production config
5. Deploys to `gh-pages` branch using gh-pages package

## Troubleshooting

- **Build fails**: Check that all dependencies are properly installed
- **Pages not updating**: Wait a few minutes after deployment, GitHub Pages can take time to update
- **404 on sub-pages**: This is expected with SPA routing, the main page should load correctly
- **Backend issues**: Ensure Python 3.13+ is installed and virtual environment is working

## Next Steps

1. Push your code to the `dev` branch to trigger the first deployment
2. Configure GitHub Pages settings in your repository
3. Start your backend using the provided scripts when developing locally