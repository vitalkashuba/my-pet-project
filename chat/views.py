from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.utils.text import slugify
from .models import Room, Message

@login_required
def map_view(request):
    return render(request, 'chat/map.html') 
    
@login_required
def index(request):
    rooms = Room.objects.all()
    return render(request, 'chat/index.html', {'rooms': rooms})


@login_required
def room(request, room_slug):
    room = get_object_or_404(Room, slug=room_slug)
    history = room.get_last_messages(50)
    return render(request, 'chat/room.html', {
        'room': room,
        'history': history,
    })


@login_required
def create_room(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        if name:
            slug = slugify(name)
            room, created = Room.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': description, 'created_by': request.user}
            )
            if not created:
                messages.error(request, 'Кімната з такою назвою вже існує.')
            return redirect('room', room_slug=room.slug)
    return render(request, 'chat/create_room.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if not username:
            messages.error(request, 'Введіть імʼя користувача.')
        elif password1 != password2:
            messages.error(request, 'Паролі не збігаються.')
        elif User.objects.filter(username=username).exists():
            messages.error(request, 'Такий користувач вже існує.')
        else:
            user = User.objects.create_user(username=username, password=password1)
            messages.success(request, 'Акаунт створено! Увійдіть.')
            return redirect('login')
    return render(request, 'register.html')
