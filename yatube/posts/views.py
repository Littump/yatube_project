from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow

CNT_POSTS = 10


@cache_page(20)
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
    cnt_posts_user = user.posts.count()
    is_following = (request.user.is_authenticated
                    and Follow.objects.filter(
                        user=request.user,
                        author=user
                    ).exists())
    context = {
        'page_obj': page_obj,
        'cnt_posts_user': cnt_posts_user,
        'author': user,
        'following': is_following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    author = post.author
    cnt_posts_user = author.posts.count()
    comments = post.comments.all()
    form_comment = CommentForm()
    context = {
        'post': post,
        'cnt_posts_user': cnt_posts_user,
        'form': form_comment,
        'comments': comments
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    user = request.user
    if request.method == 'POST':
        form = PostForm(request.POST, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = user
            post.save()
            url = reverse('posts:profile', args=[user.username])
            return redirect(url)
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    user = request.user
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    if user != author:
        return redirect('posts:post_detail', post_id=post.pk)
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post.pk)
    else:
        form = PostForm(instance=post)
    return render(request, 'posts/create_post.html',
                  {'form': form, 'is_edit': 1, 'post_id': post_id})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, CNT_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    url = reverse('posts:profile', args=[username])
    return redirect(url)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    Follow.objects.filter(user=request.user, author=author).delete()
    url = reverse('posts:profile', args=[username])
    return redirect(url)
