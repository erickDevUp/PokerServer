from django.http import JsonResponse
from .models import Rooms_01
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
import redis
# Create your views here.
import redis


def home(request):
    rooms = Rooms_01.objects.all()
    rooms_list = [room.to_dict() for room in rooms]
  
    context = {'rooms': rooms_list}
  
    return JsonResponse(context)

def room(request,room_id):
    try:
        room = request.user.rooms_joined.get(id=room_id)
    except Rooms_01.DoesNotExist:
        return HttpResponseForbidden()
    
    context = {'room': room.to_dict()}
    return JsonResponse(context)
    