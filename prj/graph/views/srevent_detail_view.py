from django.views.generic import DetailView
from graph.models import SREvent

class SREventDetailView(DetailView):
    template_name = 'graph/srevent_detail.html'
    model = SREvent
