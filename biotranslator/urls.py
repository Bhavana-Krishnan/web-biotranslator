from django.urls import path
from .views import TranslateDNAView, DNAHistoryListView, SignUpView 

urlpatterns = [
    path('', TranslateDNAView.as_view(), name='DNA'),
    path('history/', DNAHistoryListView.as_view(), name='history'),
    path('signup/', SignUpView.as_view(), name='signup'), 
]