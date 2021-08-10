from django.shortcuts import render, get_object_or_404

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
    stream = get_object_or_404(Stream, pk=stream_id)
    return render(request, 'spotify_stats/detail.html', {'stream': stream})


def more_detail(request, track_id):
    response = "You're looking at the more details of track %s."
    return HttpResponse(response % track_id)

