import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View

# Constants
GOOGLE_CLIENT_SECRETS_PATH = os.getenv('GOOGLE_CLIENT_SECRETS_PATH')
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Initiates the Google Calendar Integration Request
class GoogleCalendarInitView(View):
  def get(self, request):
    flow = Flow.from_client_secrets_file(
      GOOGLE_CLIENT_SECRETS_PATH,
      scopes=SCOPES
    )
    flow.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    authorization_url, state = flow.authorization_url(
      access_type = 'offline',
      include_granted_scopes = 'true',
      prompt='consent'
    )
    # Storing state in the session to prevent CSRF attacks
    request.session['state'] = state
    return HttpResponseRedirect(authorization_url)

class GoogleCalendarRedirectView(View):
  def get(self, request):
    state = request.session.get('state', None)
    if state is None or state != request.GET.get('state'):
      return JsonResponse({'error': 'Unauthorized Access'}, status=401)

    if request.GET.get('error') is not None and request.GET.get('error') == 'access_denied':
      return JsonResponse({'error': 'Permission denied'}, status=403)
    elif request.GET.get('error') is not None:
      return JsonResponse({'error': request.GET.get('error')}, status=401)

    flow = Flow.from_client_secrets_file(
      GOOGLE_CLIENT_SECRETS_PATH,
      SCOPES,
      state=state
    )
    flow.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI')
    request_uri = request.build_absolute_uri().split(':')
    request_uri[0] = 'https'
    request_uri = ':'.join(request_uri)
    try:
      flow.fetch_token(
        authorization_response=request_uri
      )
    except:
      return JsonResponse({'error': 'Authentication expired, please authenticate again.'}, status=403)
    else:  
      creds = flow.credentials
      credentials = {'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes}
      request.session['credentials'] = credentials

    try:
      service = build('calendar', 'v3', credentials=Credentials(**request.session['credentials']), static_discovery=False)
  
      events = []
      
      response = service.events().list(calendarId='primary', singleEvents=True, orderBy='startTime').execute()
      events = response.get('items', [])
      if not events:
        return JsonResponse({'events': []})
      
      return JsonResponse({'events': events})
    except HttpError as error:
      return JsonResponse({'error': error}, status=500)
      
