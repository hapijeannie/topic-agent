"""HTTP-level access checks with synthetic sessions; no real OAuth credentials."""

from base64 import b64encode
import json
import time
import unittest
from unittest.mock import AsyncMock, patch
from urllib.parse import parse_qs, urlparse

from fastapi.testclient import TestClient
from itsdangerous import TimestampSigner
from unittest.mock import MagicMock

import main


SETTINGS = {
    'APP_URL': 'http://localhost:3000',
    'SESSION_SECRET': 'test-only-session-secret-not-a-real-secret',
    'GITHUB_CLIENT_ID': 'test-client',
    'GITHUB_CLIENT_SECRET': 'test-secret',
    'GITHUB_ALLOWED_USER_ID': '123',
}


def session_cookie(user_id='123', expires=None):
    data = {'user': {'id': user_id, 'login': 'test-owner'},
            'expires_at': expires if expires is not None else int(time.time()) + 300}
    encoded = b64encode(json.dumps(data).encode())
    return TimestampSigner(SETTINGS['SESSION_SECRET']).sign(encoded).decode()


class AuthTests(unittest.TestCase):
    def setUp(self):
        self.app = main.create_app(SETTINGS)
        self.client = TestClient(self.app)
        self.addCleanup(self.client.close)

    def test_anonymous_cannot_read_or_write_documents(self):
        with patch.object(main, 'open_connection', side_effect=AssertionError('must not connect')):
            for path in ('/documents', '/documents/1'):
                self.assertEqual(self.client.get(path).status_code, 401)
            self.assertEqual(self.client.post('/documents', json={}).status_code, 401)
        self.assertEqual(self.client.get('/health').status_code, 200)

    def test_bad_expired_and_other_owner_sessions_are_denied(self):
        for cookie, status in ((session_cookie() + 'bad', 401),
                               (session_cookie(expires=0), 401),
                               (session_cookie('999'), 403)):
            self.client.cookies.set('fuxi_session', cookie)
            self.assertEqual(self.client.get('/documents').status_code, status)

    def test_owner_session_and_logout(self):
        self.client.cookies.set('fuxi_session', session_cookie(), domain='testserver.local', path='/')
        response = self.client.get('/auth/me')
        self.assertEqual(response.json(), {'id': '123', 'login': 'test-owner'})
        self.assertEqual(response.headers['cache-control'], 'no-store')
        self.assertEqual(self.client.post('/auth/logout', headers={'Origin': SETTINGS['APP_URL']}).status_code, 200)
        self.assertEqual(self.client.get('/auth/me').status_code, 401)

    def test_owner_write_requires_exact_origin(self):
        self.client.cookies.set('fuxi_session', session_cookie())
        for origin in ('https://evil.example', None):
            headers = {'Origin': origin} if origin else {}
            self.assertEqual(self.client.post('/documents', headers=headers, json={}).status_code, 403)

    def test_missing_config_is_closed(self):
        with TestClient(main.create_app({})) as client:
            self.assertEqual(client.get('/documents').status_code, 503)
            self.assertEqual(client.get('/health').status_code, 200)

    def test_login_has_state_pkce_and_fixed_callback(self):
        response = self.client.get('/auth/login', follow_redirects=False)
        query = parse_qs(urlparse(response.headers['location']).query)
        self.assertEqual(query['redirect_uri'], [SETTINGS['APP_URL'] + '/backend/auth/callback'])
        self.assertTrue(query['state'][0])
        self.assertEqual(query['code_challenge_method'], ['S256'])
        self.assertIn('httponly', response.headers['set-cookie'].lower())

    def test_callback_without_state_does_not_authenticate(self):
        response = self.client.get('/auth/callback?code=fake', follow_redirects=False)
        self.assertIn('error=failed', response.headers['location'])
        self.assertEqual(self.client.get('/auth/me').status_code, 401)

    def test_callback_allows_only_configured_owner_and_does_not_store_token(self):
        github = self.app.state.oauth.create_client('github')
        for user_id, error in ((999, True), (123, False)):
            profile = unittest.mock.Mock()
            profile.json.return_value = {'id': user_id, 'login': 'test-owner'}
            with patch.object(github, 'authorize_access_token', new=AsyncMock(return_value={'access_token': 'synthetic-private-token'})), \
                 patch.object(github, 'get', new=AsyncMock(return_value=profile)):
                response = self.client.get('/auth/callback', follow_redirects=False)
            self.assertEqual('error=denied' in response.headers['location'], error)
            self.assertEqual(self.client.get('/auth/me').status_code, 401 if error else 200)
            self.assertNotIn('synthetic-private-token', response.headers.get('set-cookie', ''))

    def test_authorized_routes_pagination_and_missing_detail(self):
        self.client.cookies.set('fuxi_session', session_cookie())
        with patch.object(main, 'open_connection', return_value=MagicMock()), \
             patch.object(main, 'list_documents', return_value={'items': [], 'has_more': False}) as listing, \
             patch.object(main, 'get_document', return_value=None):
            self.assertEqual(self.client.get('/documents?limit=0').status_code, 422)
            self.assertEqual(self.client.get('/documents?limit=101').status_code, 422)
            self.assertEqual(self.client.get('/documents?offset=-1').status_code, 422)
            self.assertEqual(self.client.get('/documents?limit=10&offset=20').json(), {'items': [], 'has_more': False})
            self.assertEqual(listing.call_args.args[1:], (10, 20))
            self.assertEqual(self.client.get('/documents/123').status_code, 404)

    def test_authorized_upload_returns_updated(self):
        self.client.cookies.set('fuxi_session', session_cookie())
        raw = '---\ntitle: test\nslug: test\n---\nbody\n'
        with patch.object(main, 'open_connection', return_value=MagicMock()), \
             patch.object(main, 'save_document', return_value={'status': 'updated', 'article_id': 1, 'chunk_count': 1}):
            response = self.client.post('/documents', headers={'Origin': SETTINGS['APP_URL']}, json={
                'raw': raw, 'source_namespace': 'test', 'ownership': 'owned', 'source_path': 'test.md'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'updated')

    def test_https_session_cookie_is_secure(self):
        with TestClient(main.create_app(dict(SETTINGS, APP_URL='https://library.example'))) as client:
            response = client.get('/auth/login', follow_redirects=False)
        self.assertIn('secure', response.headers['set-cookie'].lower())
        self.assertIn('samesite=lax', response.headers['set-cookie'].lower())
