from django.urls import path
from ref.views import (
    phone_auth, 
    code_auth, 
    profile, 
    activate_invite
)

urlpatterns = [
    path('', phone_auth, name='phone_auth'),
    path('code/', code_auth, name='code_auth'),
    path('profile/', profile, name='profile'),
    path('activate-invite/', activate_invite, name='activate_invite'),
]