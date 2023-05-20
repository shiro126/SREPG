from django.views.generic import ListView
from graph.models import SREvent

class SREventListView(ListView):
    template_name = 'graph/srevent_list.html'
    model = SREvent

    def get_queryset(self, **kwargs):
        queryset = super().get_queryset(**kwargs)
        queryset = queryset.filter(is_published=True).order_by('-start_dt')
        return queryset
