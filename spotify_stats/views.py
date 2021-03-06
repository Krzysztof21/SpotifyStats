from urllib.parse import urlencode

from django.shortcuts import render, get_object_or_404, redirect, reverse

from django.http import HttpResponseRedirect

from django.views import View, generic
from django.views.generic.edit import FormView
from django.views.generic.list import ListView

from .models import Stream, Track
from .forms import DateForm
from .utils import milliseconds_to_hh_mm_ss


def index(request):
    return render(request, 'spotify_stats/index.html')


class TrackDetailView(generic.DetailView):
    model = Track
    template_name = 'spotify_stats/track_detail.html'


class StreamDetailView(generic.DetailView):
    model = Stream
    template_name = 'spotify_stats/stream_detail.html'


class PickDateFormView(FormView):
    template_name = 'spotify_stats/pick_date.html'
    form_class = DateForm

    def get_success_url(self, form):
        base_url = reverse('spotify_stats:most_listened')
        query_string = urlencode({
            'start_time': form.cleaned_data["start_date"].strftime('%Y-%m-%d %H:%M%z'),
            'end_time': form.cleaned_data["end_date"].strftime('%Y-%m-%d %H:%M%z'),
            'include_podcasts': form.cleaned_data['include_podcasts'],
            'limit': form.cleaned_data['limit'],
            'order': form.cleaned_data['order']})
        return '{}?{}'.format(base_url, query_string)

    def form_valid(self, form):
        return HttpResponseRedirect(self.get_success_url(form))


# TODO: refactor
class MostListenedListView(ListView):
    template_name = 'spotify_stats/most_listened.html'
    context_object_name = 'streams'

    def get_queryset(self):
        start_time = self.request.GET['start_time'][:10]
        end_time = self.request.GET['end_time'][:10]
        include_podcasts = self.request.GET['include_podcasts']
        podcast_filter = '' if include_podcasts == 'True' else "WHERE t.album_name IS NOT 'None'"
        limit = self.request.GET['limit']
        order = self.request.GET['order']
        query = f'''
                SELECT s.id, s.track_id, t.track_name, s.total_time, t.album_name, s.no_streams FROM
                    (SELECT sum(ms_played) AS total_time, count(id) AS no_streams, id, track_id FROM stream
                        WHERE end_time >= "{start_time}" AND end_time < "{end_time}" GROUP BY track_id) AS s
                    JOIN track AS t ON s.track_id=t.id
                    {podcast_filter}
                    ORDER BY s.{order} DESC
                    LIMIT {limit};  
                '''
        streams = list(Stream.objects.raw(query))
        for s in streams:
            t = milliseconds_to_hh_mm_ss(s.total_time)
            s.total_time = f'{t[0]}:{t[1]}:{t[2]}'
        return streams


class BasicStats(View):

    @staticmethod
    def get(request, track_id):
        track = get_object_or_404(Track, pk=track_id)
        stats = {
            'total_streams': Stream.objects.get_total_streams(track_id),
            'total_time_listened': Stream.objects.get_total_time_listened(track_id),
            'last_week_streams': Stream.objects.get_number_last_week_streams(track_id)
        }
        context = {
            'track': track,
            'stats': stats
        }
        return render(request, 'spotify_stats/basic_stats.html', context)
