import datetime as dt

from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from django.db.models import Count, Sum

from .models import Stream, Track
from .forms import DateForm


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
    total_time_listened = Stream.objects.filter(track_id=track_id).aggregate(Sum('ms_played'))
    context = {
        'track': track,
        'total_streams': total_streams['id__count'],
        'total_time_listened': total_time_listened['ms_played__sum'],
        'last_week_streams': last_week_streams['id__count']}
    return render(request, 'spotify_stats/basic_stats.html', context)


def pick_date(request):
    if request.method == 'POST':
        form = DateForm(request.POST)
        if form.is_valid():
            start = form.cleaned_data["start_date"]
            end = form.cleaned_data["end_date"]
            return HttpResponseRedirect(f'/most_listened?start_time={start}&end_time={end}')
    else:
        form = DateForm()
    return render(request, 'spotify_stats/pick_date.html', {'form': form})

# write a form view where you can enter time range
# and on the next page you'll get 5 most listened tracks

