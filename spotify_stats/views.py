from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, Http404
from django.template import loader
from django.db.models import Count

from .models import Stream, Track


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
    total = Stream.objects.filter(track_id=track_id).aggregate(Count('id'))
    # no of streams of this track last week
    # total time listened
    return render(request, 'spotify_stats/basic_stats.html', {'track': track, 'total': total})

# write a form view where you can enter time range
# and on the next page youll get 5 most listened tracks
