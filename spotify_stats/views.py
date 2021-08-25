from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views import View
from django.db.models import Count, Sum

from .models import Stream, Track
from .forms import DateForm
from .utils import milliseconds_to_hh_mm_ss


def index(request):
    longest_streams_list = Stream.objects.order_by('-ms_played')[:5]
    context = {
        'longest_streams_list': longest_streams_list,
    }
    return render(request, 'spotify_stats/index.html', context)


def detail(request, stream_id):
    stream = Stream.objects.filter(id=stream_id).first()
    if stream is None:
        raise Http404("Stream with this ID does not exist")
    track = Track.objects.filter(stream__id=stream_id).first()
    return render(request, 'spotify_stats/detail.html', {'stream': stream, 'track': track})


# TODO: is this url call good practice?
def pick_date(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            frmt = '%Y-%m-%d %H:%M'
            start = form.cleaned_data["start_date"].strftime(frmt)
            end = form.cleaned_data["end_date"].strftime(frmt)
            include_podcasts = form.cleaned_data['include_podcasts']
            limit = form.cleaned_data['limit']
            order = form.cleaned_data['order']
            url = f'/spotify_stats/most_listened?start_time={start}&end_time={end}&' \
                + f'include_podcasts={include_podcasts}&limit={limit}&order={order}'
            return HttpResponseRedirect(url)
    else:
        form = DateForm()
    return render(request, 'spotify_stats/pick_date.html', {'form': form})


# TODO: refactor
def most_listened(request):
    start_time = request.GET.get('start_time')[:10]
    end_time = request.GET.get('end_time')[:10]
    include_podcasts = request.GET.get('include_podcasts')
    podcast_filter = '' if include_podcasts == 'True' else "WHERE t.album_name IS NOT 'None'"
    limit = request.GET.get('limit')
    order = request.GET.get('order')
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
    return render(request, 'spotify_stats/most_listened.html', {'streams': streams})


class BasicStats(View):
    def get(self, request, track_id):
        track = Track.objects.filter(id=track_id).first()
        stats = {
            'total_streams': self.get_total_streams(track_id),
            'total_time_listened': self.get_total_time_listened(track_id),
            'last_week_streams': self.get_number_last_week_streams(track_id)
        }
        context = {
            'track': track,
            'stats': stats
        }
        return render(request, 'spotify_stats/basic_stats.html', context)

    def get_total_streams(self, track_id):
        return self._get_streams_for_track(track_id).aggregate(Count('id'))['id__count']

    def get_total_time_listened(self, track_id):
        time_tuple = milliseconds_to_hh_mm_ss(
            self._get_streams_for_track(track_id).aggregate(Sum('ms_played'))['ms_played__sum'])
        return f'{time_tuple[0]}:{time_tuple[1]}:{time_tuple[2]}'

    def get_number_last_week_streams(self, track_id):
        today = datetime.today().strftime('%Y-%m-%d %H:%M')
        week_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M')
        streams = self._get_streams_for_track(track_id).filter(end_time__gte=week_ago, end_time__lte=today)
        return streams.aggregate(Count('id'))['id__count']

    @staticmethod
    def _get_streams_for_track(self, track_id):
        return Stream.objects.filter(track_id=track_id)
