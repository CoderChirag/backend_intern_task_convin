import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import View

# Constants
GOOGLE_CLIENT_SECRETS_PATH = os.getenv('GOOGLE_CLIENT_SECRETS_PATH')
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

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
    request.session['state'] = state
    return HttpResponseRedirect(authorization_url)


# Create your views here.
