import datetime as dt

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
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


def more_detail(request, track_id):
    response = "You're looking at the more details of track %s."
    return HttpResponse(response % track_id)


# TODO: refactor
def basic_stats(request, track_id):
    track = Track.objects.filter(id=track_id).first()
    # no of streams of this track total
    total_streams = Stream.objects.filter(track_id=track_id).aggregate(Count('id'))
    # no of streams of this track last week
    today_tuple = dt.datetime.today().timetuple()
    today = f'{today_tuple[0]}-{today_tuple[1]}-{today_tuple[2]}'
    week_tuple = (dt.datetime.today() - dt.timedelta(days=7)).timetuple()
    week = f'{week_tuple[0]}-{week_tuple[1]}-{week_tuple[2]}'
    last_week_streams = Stream.objects.filter(track_id=track_id).filter(end_time__gte=week, end_time__lte=today).aggregate(Count('id'))
    # total time listened
    time_tuple = milliseconds_to_hh_mm_ss(Stream.objects.filter(track_id=track_id).aggregate(Sum('ms_played'))['ms_played__sum'])
    total_time_listened = f'{time_tuple[0]}:{time_tuple[1]}:{time_tuple[2]}'
    context = {
        'track': track,
        'total_streams': total_streams['id__count'],
        'total_time_listened': total_time_listened,
        'last_week_streams': last_week_streams['id__count']}
    return render(request, 'spotify_stats/basic_stats.html', context)


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

