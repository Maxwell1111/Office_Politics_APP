"""
OAuth API routes for Google Workspace integration
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from typing import Optional

from subtext.google_oauth import google_oauth_service

router = APIRouter(tags=["oauth"])

# Store state for CSRF protection (in-memory, replace with Redis in production)
oauth_states = {}


@router.get("/oauth/google/authorize")
async def google_oauth_authorize(
    user_id: Optional[str] = Query(None, description="Optional user ID to associate tokens with")
) -> RedirectResponse:
    """
    Initiate Google OAuth flow

    This redirects the user to Google's consent screen where they can
    authorize access to Gmail metadata and Calendar events.

    After authorization, Google redirects back to /oauth/google/callback

    Scopes requested:
    - gmail.metadata: Read email headers only (no body content)
    - calendar.events.readonly: Read calendar events
    - userinfo.email: Get user's email address
    """

    try:
        # Generate state for CSRF protection
        import uuid
        state = str(uuid.uuid4())

        # Store state with user_id
        oauth_states[state] = {
            "user_id": user_id or "default_user",
            "timestamp": __import__('datetime').datetime.now()
        }

        # Get authorization URL
        auth_url = google_oauth_service.get_authorization_url(state=state)

        return RedirectResponse(url=auth_url)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate OAuth: {str(e)}"
        )


@router.get("/oauth/google/callback")
async def google_oauth_callback(
    code: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    error: Optional[str] = Query(None)
) -> HTMLResponse:
    """
    Google OAuth callback endpoint

    This is where Google redirects the user after authorization.
    We exchange the authorization code for access and refresh tokens.
    """

    # Handle OAuth error
    if error:
        return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>OAuth Error</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        text-align: center;
                    }}
                    .error {{
                        color: #dc2626;
                        background: #fef2f2;
                        padding: 20px;
                        border-radius: 8px;
                        border: 1px solid #fecaca;
                    }}
                    .btn {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: #1a73e8;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>❌ Authorization Failed</h2>
                    <p>Error: {error}</p>
                    <p>You denied access or there was an error during authorization.</p>
                </div>
                <a href="/automated-power-map.html" class="btn">Back to Power Map</a>
            </body>
            </html>
        """, status_code=400)

    # Validate code and state
    if not code or not state:
        raise HTTPException(
            status_code=400,
            detail="Missing code or state parameter"
        )

    # Verify state (CSRF protection)
    if state not in oauth_states:
        raise HTTPException(
            status_code=400,
            detail="Invalid state parameter - possible CSRF attack"
        )

    state_data = oauth_states.pop(state)  # Remove state after use
    user_id = state_data["user_id"]

    try:
        # Exchange code for tokens
        tokens = google_oauth_service.exchange_code_for_tokens(code)

        # Get user's email
        user_email = google_oauth_service.get_user_email(tokens["access_token"])

        # Store tokens
        google_oauth_service.store_tokens(user_id, tokens)

        # Return success page
        return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>OAuth Success</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        text-align: center;
                    }}
                    .success {{
                        color: #166534;
                        background: #f0fdf4;
                        padding: 20px;
                        border-radius: 8px;
                        border: 1px solid #bbf7d0;
                    }}
                    .info {{
                        background: #f8fafc;
                        padding: 15px;
                        border-radius: 6px;
                        margin: 20px 0;
                        font-size: 0.875rem;
                        color: #475569;
                    }}
                    .btn {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: #1a73e8;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        font-weight: 500;
                    }}
                    .btn:hover {{
                        background: #1557b0;
                    }}
                </style>
            </head>
            <body>
                <div class="success">
                    <h2>✅ Authorization Successful!</h2>
                    <p>Connected to: <strong>{user_email}</strong></p>
                    <p>Your Gmail and Calendar are now connected.</p>
                </div>

                <div class="info">
                    <p><strong>Privacy Notice:</strong></p>
                    <p>We only read email metadata (From/To/CC/timestamps).</p>
                    <p>Email body content is NEVER accessed or stored.</p>
                    <p>You can revoke access anytime from your Google Account settings.</p>
                </div>

                <a href="/automated-power-map.html?connected=true&email={user_email}" class="btn">
                    Generate Power Map →
                </a>
            </body>
            </html>
        """)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>OAuth Error</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                        max-width: 600px;
                        margin: 50px auto;
                        padding: 20px;
                        text-align: center;
                    }}
                    .error {{
                        color: #dc2626;
                        background: #fef2f2;
                        padding: 20px;
                        border-radius: 8px;
                        border: 1px solid #fecaca;
                    }}
                    code {{
                        background: #1e293b;
                        color: #e2e8f0;
                        padding: 2px 6px;
                        border-radius: 4px;
                        font-size: 0.875rem;
                    }}
                    .btn {{
                        display: inline-block;
                        margin-top: 20px;
                        padding: 10px 20px;
                        background: #1a73e8;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                    }}
                </style>
            </head>
            <body>
                <div class="error">
                    <h2>❌ Failed to Complete Authorization</h2>
                    <p>Error: <code>{str(e)}</code></p>
                    <p style="font-size: 0.875rem; margin-top: 1rem;">
                        This might be due to missing Google OAuth credentials.
                        Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are set.
                    </p>
                </div>
                <a href="/automated-power-map.html" class="btn">Back to Power Map</a>
            </body>
            </html>
        """, status_code=500)


@router.post("/oauth/google/revoke")
async def revoke_google_oauth(user_id: str = "default_user") -> dict:
    """
    Revoke Google OAuth tokens

    This disconnects the user's Google account and deletes stored tokens.
    """

    try:
        success = google_oauth_service.revoke_tokens(user_id)

        if success:
            return {
                "status": "success",
                "message": "Google account disconnected successfully"
            }
        else:
            return {
                "status": "not_found",
                "message": "No connected Google account found"
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to revoke tokens: {str(e)}"
        )


@router.get("/oauth/google/status")
async def google_oauth_status(user_id: str = "default_user") -> dict:
    """
    Check if user has connected Google account

    Returns OAuth status and available scopes
    """

    access_token = google_oauth_service.get_valid_access_token(user_id)

    if access_token:
        try:
            user_email = google_oauth_service.get_user_email(access_token)
            return {
                "connected": True,
                "user_email": user_email,
                "scopes": google_oauth_service.scopes
            }
        except Exception:
            return {
                "connected": False,
                "message": "Token expired or invalid"
            }
    else:
        return {
            "connected": False,
            "message": "No Google account connected"
        }
