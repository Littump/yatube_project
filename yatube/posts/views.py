from django.shortcuts import render, get_object_or_404
from .models import Post, Group

def index(request):
    posts = Post.objects.order_by('-pub_date')[:10]
    # title = 'Это главная страница проекта Yatube'
    # context = {
    #     'title': title,
    # }
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context) 

def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    # title = 'Здесь будет информация о группах проекта Yatube'
    # context = {
    #     'title': title,
    # }
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context) 