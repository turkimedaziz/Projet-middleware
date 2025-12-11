from django.urls import path
from mqttmiddleware import views

urlpatterns = [
    # Simple dashboard for viewing recent middleware messages
    path('dashboard/', views.dashboard, name='dashboard'),
]
