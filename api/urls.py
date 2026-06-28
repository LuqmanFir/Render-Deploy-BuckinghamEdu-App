
from django.urls import path
from .views import PiGroupCalculatorView

urlpatterns = [
    path('pi-groups/', PiGroupCalculatorView.as_view(), name='pi-groups-calculator')
]