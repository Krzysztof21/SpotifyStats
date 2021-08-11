from django.shortcuts import render, get_object_or_404

from django.http import HttpResponse, Http404
from django.template import loader

from .models import Stream, Track


def index(request):
    longest_streams_list = Stream.objects.order_by('-ms_played')[:5]
    context = {
        'longest_streams_list': longest_streams_list,
    }
    return render(request, 'spotify_stats/index.html', context)


def detail(request, stream_id):
    #stream = get_object_or_404(Stream, pk=stream_id)
    #stream = Stream.objects.filter(id=stream_id).prefetch_related('track__id_set','track_set')
    #stream = Stream.objects.select_related('track__track_name').get(id=stream_id)
    stream = Stream.objects.filter(id=stream_id).first()
    track = list(Stream.objects.filter(track__id=stream_id).first())
    track_name = stream.ms_played
    #artist_name
    #album_name
    #min_played
    return render(request, 'spotify_stats/detail.html', {'stream': stream})


def more_detail(request, track_id):
    response = "You're looking at the more details of track %s."
    return HttpResponse(response % track_id)

# write a form view where you can enter time range
# and on the next page youll get 5 most listened tracks