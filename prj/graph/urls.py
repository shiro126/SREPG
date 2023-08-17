from django.urls import path
from graph.views import SREventListView, SREventDetailView

app_name = 'graph'
urlpatterns = [
    path('', SREventListView.as_view(),name='index'),
    path('<int:event_id>/',SREventDetailView.as_view(),name='detail'),
]
