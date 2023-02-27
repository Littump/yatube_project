from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

CNT_POSTS = 10


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, CNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, CNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.all()
    paginator = Paginator(post_list, CNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    cnt_posts_user = len(post_list)
    context = {
        'page_obj': page_obj,
        'cnt_posts_user': cnt_posts_user,
        'username': username,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    cnt_posts_user = author.posts.count()
    context = {
        'post': post,
        'cnt_posts_user': cnt_posts_user,
    }
    return render(request, 'posts/post_detail.html', context)


def post_create(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            return redirect(f'/profile/{user.username}/')
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


def post_edit(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    if user != author:
        return post_detail(request, post_id)
    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': 1, 'post_id': post_id})
