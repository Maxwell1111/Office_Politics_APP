# Google OAuth Setup Guide

This guide explains how to set up Google OAuth for automated power map generation from Gmail and Calendar data.

## 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Name it "Office Politics App" (or your preferred name)

## 2. Enable Required APIs

1. In the Google Cloud Console, go to **APIs & Services** > **Library**
2. Search for and enable these APIs:
   - **Gmail API**
   - **Google Calendar API**
   - **Google OAuth2 API** (People API)

## 3. Configure OAuth Consent Screen

1. Go to **APIs & Services** > **OAuth consent screen**
2. Select **External** user type (or Internal if you have a Google Workspace)
3. Fill in the required fields:
   - **App name**: Office Politics
   - **User support email**: Your email
   - **Developer contact**: Your email
4. Add scopes:
   - `https://www.googleapis.com/auth/gmail.metadata` (Read email headers only)
   - `https://www.googleapis.com/auth/calendar.events.readonly` (Read calendar events)
   - `https://www.googleapis.com/auth/userinfo.email` (Get user email)
5. Add test users (your email) if in testing mode
6. Save and continue

## 4. Create OAuth 2.0 Credentials

1. Go to **APIs & Services** > **Credentials**
2. Click **Create Credentials** > **OAuth 2.0 Client ID**
3. Application type: **Web application**
4. Name: "Office Politics Web App"
5. Add **Authorized redirect URIs**:
   - For local development: `http://localhost:8000/api/oauth/google/callback`
   - For production (Render): `https://your-app.onrender.com/api/oauth/google/callback`
6. Click **Create**
7. **Save the Client ID and Client Secret** (you'll need these)

## 5. Set Environment Variables

### Local Development (.env file)

Create or update `.env` in the project root:

```bash
# Google OAuth Credentials
GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8000/api/oauth/google/callback
```

### Production (Render.com)

1. Go to your Render dashboard
2. Select your service
3. Click **Environment**
4. Add environment variables:
   ```
   GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   GOOGLE_REDIRECT_URI=https://your-app.onrender.com/api/oauth/google/callback
   ```
5. Save changes (this will trigger a redeploy)

## 6. Test the OAuth Flow

### Local Testing

1. Start the app: `./prod` or `python prod.py`
2. Visit: `http://localhost:8000/automated-power-map.html`
3. Click **"Connect Google Account"**
4. You should be redirected to Google's consent screen
5. After authorization, you'll be redirected back to the app
6. Click **"Generate Power Map"** to analyze your real data

### Production Testing

1. Visit: `https://your-app.onrender.com/automated-power-map.html`
2. Follow the same steps as local testing

## 7. Privacy & Scopes Explained

### What Data We Access

✅ **Gmail Metadata (gmail.metadata scope)**:
- From/To/CC email addresses
- Email timestamps
- Thread IDs
- Subject lines (optional, not currently used)

❌ **What We DON'T Access**:
- Email body content
- Email attachments
- Spam/Trash folders

✅ **Calendar Events (calendar.events.readonly)**:
- Meeting titles
- Start/end times
- Attendee lists
- Meeting locations

✅ **User Info (userinfo.email)**:
- Just your email address to identify you

### How We Use This Data

1. **Email Metadata**: Build network graph of who you communicate with
2. **Calendar Events**: Identify meeting clusters and collaboration patterns
3. **Graph Analysis**: Calculate centrality, betweenness, structural holes
4. **AI Insights**: Generate strategic recommendations

### Data Storage

- **Tokens**: Stored in-memory (currently) or encrypted database (production)
- **Email/Calendar Data**: NOT stored, only processed in real-time
- **Network Graph**: Aggregated metadata only (no content)

## 8. Troubleshooting

### "redirect_uri_mismatch" Error

**Problem**: The redirect URI doesn't match what's configured in Google Cloud Console

**Solution**:
1. Check that `GOOGLE_REDIRECT_URI` environment variable matches exactly
2. Verify the redirect URI is added in Google Cloud Console
3. Make sure there are no trailing slashes

### "invalid_client" Error

**Problem**: Client ID or Client Secret is incorrect

**Solution**:
1. Double-check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`
2. Make sure you copied the entire value (no spaces)
3. Regenerate credentials if needed

### "access_denied" Error

**Problem**: User denied permission or app not verified

**Solution**:
1. Make sure you added your email as a test user
2. App must be in "Testing" mode to work with test users
3. Eventually submit for verification for public use

### OAuth Works Locally But Not in Production

**Problem**: Different redirect URI or missing environment variables

**Solution**:
1. Add production redirect URI to Google Cloud Console:
   `https://your-app.onrender.com/api/oauth/google/callback`
2. Set environment variables in Render dashboard
3. Redeploy the app

## 9. Moving to Production

### Before Public Launch

1. **Verify Your App**: Submit OAuth app for verification in Google Cloud Console
2. **Update Privacy Policy**: Add a privacy policy URL
3. **Terms of Service**: Add terms of service URL
4. **Change to Production**: Move from "Testing" to "In Production" mode

### Security Considerations

1. **Store tokens securely**: Use database with encryption (not in-memory)
2. **Implement token refresh**: Automatically refresh expired tokens
3. **Add rate limiting**: Prevent abuse of OAuth endpoints
4. **Use HTTPS only**: Ensure all OAuth redirects use HTTPS
5. **Add CSRF protection**: Validate state parameter properly

## 10. API Endpoints

Once configured, these endpoints will work:

- `GET /api/oauth/google/authorize` - Initiate OAuth flow
- `GET /api/oauth/google/callback` - OAuth callback (automatic)
- `GET /api/oauth/google/status` - Check connection status
- `POST /api/oauth/google/revoke` - Disconnect account
- `POST /api/automated-power-map/generate-from-oauth` - Generate power map from real data

## 11. Example OAuth Flow

```
User clicks "Connect Google Account"
  ↓
Redirect to /api/oauth/google/authorize
  ↓
Redirect to Google consent screen
  ↓
User approves scopes
  ↓
Google redirects to /api/oauth/google/callback?code=...
  ↓
Exchange code for access_token and refresh_token
  ↓
Store tokens (in-memory or database)
  ↓
Redirect to /automated-power-map.html?connected=true
  ↓
Auto-generate power map using stored token
```

## 12. Cost

Google OAuth and API usage is **FREE** for normal usage levels:
- Gmail API: 1 billion quota units/day (FREE)
- Calendar API: 1 million queries/day (FREE)
- OAuth: Unlimited (FREE)

For this app, you'll use approximately:
- Gmail metadata fetch (500 emails): ~500 quota units
- Calendar events (30 days): ~1 query

**You will NOT hit any limits with normal personal use.**

---

## Questions?

- Google OAuth Docs: https://developers.google.com/identity/protocols/oauth2
- Gmail API: https://developers.google.com/gmail/api
- Calendar API: https://developers.google.com/calendar/api
