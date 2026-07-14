import os
import requests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
print('OLLAMA_BASE_URL', settings.OLLAMA_BASE_URL)
print('OLLAMA_MODEL', settings.OLLAMA_MODEL)
print('OLLAMA_TIMEOUT_SECONDS', settings.OLLAMA_TIMEOUT_SECONDS)
print('OLLAMA_REQUEST_RETRIES', settings.OLLAMA_REQUEST_RETRIES)
print('OLLAMA_THINK', settings.OLLAMA_THINK)
print('Testing Ollama version endpoint...')
try:
    r = requests.get(settings.OLLAMA_BASE_URL + '/api/version', timeout=5)
    print('status', r.status_code)
    try:
        print('version response', r.json())
    except Exception as e:
        print('version text', r.text[:200])
except Exception as exc:
    print('OLLAMA unreachable', exc)
print('Testing generate_consultation_answer...')
from consultations.services import generate_consultation_answer
try:
    result = generate_consultation_answer('Apa itu Gerd Zero Pro?')
    print(result)
except Exception as exc:
    print('generate_consultation_answer ERROR', type(exc).__name__, exc)
