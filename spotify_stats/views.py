import datetime as dt

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.db.models import Count, Sum

from .models import Stream, Track
from .forms import DateForm
from .utils import convert_millis


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

# TODO: probably returns wrong data
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
    time_tuple = convert_millis(Stream.objects.filter(track_id=track_id).aggregate(Sum('ms_played'))['ms_played__sum'])
    total_time_listened = f'{time_tuple[0]}:{time_tuple[1]}:{time_tuple[2]}'
    context = {
        'track': track,
        'total_streams': total_streams['id__count'],
        'total_time_listened': total_time_listened,
        'last_week_streams': last_week_streams['id__count']}
    return render(request, 'spotify_stats/basic_stats.html', context)


# TODO: add "include podcasts" checkbox
def pick_date(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data["start_date"]
            end = form.cleaned_data["end_date"]
            return HttpResponseRedirect(f'/spotify_stats/most_listened?start_time={start}&end_time={end}')
    else:
        form = DateForm()
    return render(request, 'spotify_stats/pick_date.html', {'form': form})


# TODO: add logic to exclude podcasts
# TODO: refactor
def most_listened(request):
    start_time = request.GET.get('start_time')[:10]
    end_time = request.GET.get('end_time')[:10]
    streams = Stream.objects.filter(end_time__gte=start_time, end_time__lte=end_time)
    count = streams.values('track').annotate(c=Count('track')).order_by('-c')[:5]
    count_names = []
    for s in count:
        count_names.append((Track.objects.get(pk=s['track']).track_name, s['track']))
    times = streams.values('track').annotate(s=Sum('ms_played')).order_by('-s')[:5]
    times_names = []
    for s in times:
        times_names.append((Track.objects.get(pk=s['track']).track_name, s['track']))
    print(count_names)
    print(times_names)
    context = {
        'count': count,
        'count_names': count_names,
        'times': times,
        'times_names': times_names
    }
    return render(request, 'spotify_stats/most_listened.html', context)

# TODO: same as most_listened, but with arbitrary no of displayed streams