from django.shortcuts import render

from django.http import HttpResponse, Http404
from django.template import loader

from .models import Stream


def index(request):
    longest_streams_list = Stream.objects.order_by('-ms_played')[:5]
    context = {
        'longest_streams_list': longest_streams_list,
    }
    return render(request, 'spotify_stats/index.html', context)


def detail(request, stream_id):
    try:
        stream = Stream.objects.get(pk=stream_id)
    except Stream.DoesNotExist:
        raise Http404('Stream does not exist')
    return render(request, 'spotify_stats/detail.html', {'stream': stream})


def more_detail(request, track_id):
    response = "You're looking at the more details of track %s."
    return HttpResponse(response % track_id)

