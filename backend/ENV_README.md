# Backend Environment Configuration

This directory contains the environment configuration for the FastAPI backend.

## Environment Files

### `.env` (Your Active Configuration)
- **Purpose**: Main environment file used by the application
- **Location**: `backend/.env`
- **Status**: ✅ Already configured with your settings
- **Contains**: API settings, CORS origins, ML configuration, etc.

### `.env.example` (Template)
- **Purpose**: Template showing all available environment variables
- **Location**: `backend/.env.example` 
- **Usage**: Copy to `.env` and customize for your needs

## Quick Setup

If you need to recreate your `.env` file:

```bash
# In the backend directory
cd backend
cp .env.example .env
# Then edit .env with your specific settings
```

## Current Configuration

Your `.env` file is already configured with:
- ✅ **API Host**: `0.0.0.0` (accessible from network)
- ✅ **API Port**: `8000`
- ✅ **CORS Origins**: Includes GitHub Pages URL
- ✅ **ML Enabled**: `true`
- ✅ **Your IP Address**: `192.168.0.53` (in CORS settings)

## Environment Variables Explained

| Variable | Purpose | Example |
|----------|---------|---------|
| `API_HOST` | Host to bind the API server | `0.0.0.0` |
| `API_PORT` | Port for the API server | `8000` |
| `CORS_ORIGINS` | Allowed origins for CORS | `http://localhost:3000,https://yourdomain.com` |
| `ML_ENABLED` | Enable/disable ML features | `true` |
| `DEBUG` | Enable debug mode | `false` |

## Notes

- The `.env` file is ignored by git (in `.gitignore`)
- Never commit sensitive credentials to the `.env.example` file
- The application loads environment variables using `python-dotenv`