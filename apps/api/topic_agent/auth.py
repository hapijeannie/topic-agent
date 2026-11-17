"""Single-owner GitHub OAuth. No provider tokens are persisted in the session."""

import secrets
import time
from urllib.parse import urlsplit

from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import Depends, HTTPException, Request
import httpx
from starlette.middleware.sessions import SessionMiddleware
from starlette.responses import RedirectResponse


SESSION_SECONDS = 8 * 60 * 60


def require_config(request: Request):
    if not request.app.state.auth_ready:
        raise HTTPException(status_code=503, detail='Login is not configured.')


def require_owner(request: Request):
    require_config(request)
    user = request.session.get('user')
    expires = request.session.get('expires_at', 0)
    if not isinstance(user, dict) or not isinstance(expires, (int, float)) or expires <= time.time():
        raise HTTPException(status_code=401, detail='Sign in required.')
    if user.get('id') != request.app.state.owner_id:
        raise HTTPException(status_code=403, detail='Access denied.')
    if request.method not in ('GET', 'HEAD', 'OPTIONS'):
        if request.headers.get('origin') != request.app.state.app_url:
            raise HTTPException(status_code=403, detail='Invalid request origin.')
    return user


def configure_auth(app, settings):
    origin = settings.get('APP_URL', '').rstrip('/')
    parsed = urlsplit(origin)
    valid_origin = (parsed.scheme == 'https' or
                    (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1')))
    valid_origin = valid_origin and bool(parsed.netloc) and not any((parsed.path, parsed.query, parsed.fragment, parsed.username, parsed.password))
    secret = settings.get('SESSION_SECRET', '')
    owner_id = settings.get('GITHUB_ALLOWED_USER_ID', '')
    app.state.app_url = origin
    app.state.owner_id = owner_id
    app.state.auth_ready = bool(valid_origin and len(secret) >= 32 and owner_id.isdigit()
                                and settings.get('GITHUB_CLIENT_ID') and settings.get('GITHUB_CLIENT_SECRET'))
    # Missing config is fail-closed; a random fallback only keeps /health available.
    app.add_middleware(SessionMiddleware, secret_key=secret or secrets.token_urlsafe(32),
                       session_cookie='fuxi_session', max_age=SESSION_SECONDS,
                       same_site='lax', https_only=parsed.scheme == 'https')
    oauth = OAuth()
    oauth.register(
        name='github', client_id=settings.get('GITHUB_CLIENT_ID'),
        client_secret=settings.get('GITHUB_CLIENT_SECRET'),
        authorize_url='https://github.com/login/oauth/authorize',
        access_token_url='https://github.com/login/oauth/access_token',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': '', 'code_challenge_method': 'S256', 'timeout': 10},
    )
    app.state.oauth = oauth

    @app.middleware('http')
    async def no_private_cache(request, call_next):
        response = await call_next(request)
        if request.url.path != '/health':
            response.headers['Cache-Control'] = 'no-store'
        return response

    @app.get('/auth/login', dependencies=[Depends(require_config)])
    async def login(request: Request):
        request.session.clear()
        return await oauth.github.authorize_redirect(request, origin + '/backend/auth/callback')

    @app.get('/auth/callback', dependencies=[Depends(require_config)])
    async def callback(request: Request):
        try:
            token = await oauth.github.authorize_access_token(request)
            response = await oauth.github.get('user', token=token, headers={'Accept': 'application/vnd.github+json'})
            response.raise_for_status()
            profile = response.json()
            request.session.clear()
            if str(profile['id']) != owner_id:
                return RedirectResponse(origin + '/login?error=denied', status_code=303)
            request.session['user'] = {'id': owner_id, 'login': str(profile['login'])}
            request.session['expires_at'] = int(time.time()) + SESSION_SECONDS
            return RedirectResponse(origin + '/library', status_code=303)
        except (OAuthError, httpx.HTTPError, ValueError, KeyError, TypeError):
            request.session.clear()
            return RedirectResponse(origin + '/login?error=failed', status_code=303)

    @app.get('/auth/me')
    def me(user=Depends(require_owner)):
        return user

    @app.post('/auth/logout', dependencies=[Depends(require_owner)])
    def logout(request: Request):
        request.session.clear()
        return {'status': 'signed_out'}
