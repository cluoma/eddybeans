from django.db.models import Subquery, F, OuterRef, Sum, IntegerField
from django.http import HttpResponse, Http404, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect
from django.template import loader, RequestContext
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth import logout
from django.contrib.auth.models import Permission
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator

from .models import Post, Comment, LikePost, Video

import re


# def get_user_permissions(user):
#     p = Permission.objects.filter(user=user)
#     return p

def get_paginated_posts_by_day(request):
    dates = Post.objects.dates("post_date", "day", order="DESC")
    p = Paginator(dates, 3)
    page_number = request.GET.get("page", 1)
    page_obj = p.get_page(page_number)
    # print(page_obj.object_list.values('datefield'))

    posts = Post.objects.filter(post_date__date__in=page_obj.object_list.values('datefield'))\
            .order_by('-post_date')\
            .select_related('user')\
            .annotate(
        like=Subquery(
            LikePost.objects.filter(user_id=request.user, post=OuterRef("pk")).values("like")
        ),
        likes=Subquery(
            LikePost.objects.filter(post=OuterRef("pk")).values('post_id').annotate(
                likes=Sum('like', output_field=IntegerField())).values("likes")
        ),
        video_file=Subquery(
            Video.objects.filter(post=OuterRef("pk")).values('video_file')
        )
    )

    videos = Video.objects.filter(post_id__in=posts.values("id"))
    comments = Comment.objects.filter(post_id__in=posts.values("id")).select_related('user')
    likers = LikePost.objects.filter(like=1).filter(post_id__in=posts.values("id")).select_related('user')

    user_permissions = request.user.get_all_permissions()
    context = {
        'title': 'Eddybeans - Timeline',
        'user': request.user,
        'user_permissions': user_permissions,
        'page_obj': page_obj,
        'posts': posts,
        'comments': comments,
        'likers': likers,
        'videos': videos
    }
    return context

@login_required
def index(request):
    # Non-paginated version
    # posts = Post.objects.order_by('-post_date').select_related('user').annotate(
    #     like=Subquery(
    #         LikePost.objects.filter(user_id=request.user, post=OuterRef("pk")).values("like")
    #     ),
    #     likes=Subquery(
    #         LikePost.objects.filter(post=OuterRef("pk")).values('post_id').annotate(likes=Sum('like', output_field=IntegerField())).values("likes")
    #     ),
    #     video_file=Subquery(
    #         Video.objects.filter(post=OuterRef("pk"))
    #     )
    # )
    # videos = Video.objects.filter(post_id__in=posts.values("id"))
    # comments = Comment.objects.filter(post_id__in=posts.values("id")).select_related('user')
    # context = {
    #     'title': 'Eddybeans - Timeline',
    #     'user': request.user,
    #     'posts': posts,
    #     'comments': comments,
    #     'videos': videos
    # }
    context = get_paginated_posts_by_day(request)
    return render(request, 'view/index.html', context)


@login_required
def detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    template = loader.get_template('view/detail.html')
    context = {'post': post}
    return HttpResponse(template.render(context, request))


@login_required
@permission_required("view.add_post")
def submit_post(request):
    template = loader.get_template('view/submit.html')
    context = {'title': 'Eddybeans - Upload'}
    return HttpResponse(template.render(context, request))


@login_required
@permission_required("view.add_post")
def submit_new_post(request):
    if request.method == 'POST':
        # print(len(request.FILES.getlist('photo')))
        # print(request.FILES.getlist('photo')[0].content_type)
        # print(request.FILES['photo'].content_type)
        # print(request.POST)
        # print(request.POST.getlist('imgtext'))
        print("photos: ")
        print(len(request.FILES.getlist('photo')))

        # check for text only submission
        if len(request.FILES.getlist('photo')) == 0:
            p = Post(
                user=request.user,
                post_text=request.POST['text'],
                post_date=timezone.now()
            )
            p.save()
            return HttpResponseRedirect(reverse('view:index'))

        # print(request.POST)
        # print(request.FILES)
        for i, f in enumerate(request.FILES.getlist('photo')):
            print(request.POST.getlist('imgtext')[i])
            try:
                if re.match('video/', f.content_type):
                    p = Post(
                        user=request.user,
                        post_text=request.POST.getlist('imgtext')[i],
                        post_date=timezone.now()
                    )
                    p.save()
                    v = Video(
                        post=p,
                        video_file=f
                    )
                    v.save()
                else:
                    p = Post(
                        user=request.user,
                        post_text=request.POST.getlist('imgtext')[i],
                        post_date=timezone.now(),
                        post_image=f
                    )
                    p.save()
            except Exception as e:
                print(e)
                return HttpResponseBadRequest("Error")
    else:
        return HttpResponseNotAllowed(['POST'])
    return HttpResponseRedirect(reverse('view:index'))


@login_required
def submit_new_comment(request):
    if request.method == 'POST':
        try:
            current_user = request.user
            c = Comment(
                user=current_user,
                post_id=request.POST['post_id'],
                comment_text=request.POST['comment_text'],
                comment_date=timezone.now(),
                comment_likes=0
            )
            c.save()
        except:
            return HttpResponseBadRequest("Error")
    else:
            return HttpResponseNotAllowed(['POST'])
    template = loader.get_template('view/comments.html')
    posts = Post.objects.order_by('-post_date').select_related('user').filter(id=request.POST['post_id'])
    comments = Comment.objects.filter(post_id=request.POST['post_id']).select_related('user')
    context = {
        'title': 'Eddybeans - Upload',
        'posts': posts,
        'comments': comments
    }
    return HttpResponse(template.render(context, request))


@login_required
def like_post(request):
    print(request.POST)
    if request.method == 'POST':
        try:
            current_user = request.user
            like = LikePost.objects.filter(post_id=request.POST['post_id'], user_id=current_user.id).first()
            if not like:
                print("no existing like, making one")
                lp = LikePost(
                    user=current_user,
                    post_id=request.POST['post_id']
                )
                lp.save()
            else:
                if like.like:
                    like.like = False
                    print("already liked")
                else:
                    like.like = True
                    print("not liked")
                like.save()
        except:
            return HttpResponseBadRequest("Error")
    else:
            return HttpResponseNotAllowed(['POST'])
    template = loader.get_template('view/like_heart.html')
    like = LikePost.objects.filter(post_id=request.POST['post_id'], user_id=request.user.id).first()
    likes = LikePost.objects.filter(post_id=request.POST['post_id']).aggregate(likes=Sum("like", output_field=IntegerField()))
    context = {
        'title': 'Eddybeans - Upload',
        'like': like,
        'post_id': request.POST['post_id'],
        'likes': likes
    }
    return HttpResponse(template.render(context, request))


@login_required
@permission_required("view.change_post")
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    videos = Video.objects.filter(post_id=post.id)
    print(videos)

    if request.user.id != post.user_id:
        return HttpResponseRedirect(reverse('view:index'))

    user_permissions = request.user.get_all_permissions()

    template = loader.get_template('view/edit_post.html')
    context = {
        'title': 'Eddybeans - Editting',
        'user': request.user,
        'user_permissions': user_permissions,
        'post': post,
        'videos': videos
    }
    return HttpResponse(template.render(context, request))


@login_required
def post_update_text(request):
    if request.method == 'POST':

        # only the user that submitted the post can edit
        if request.user.id != request.POST['post-id']:
            return HttpResponseBadRequest("Error")

        try:
            post = get_object_or_404(Post, pk=request.POST['post-id'])
            post.post_text = request.POST['post-text']
            post.save()
        except:
            return HttpResponseBadRequest("Error")
    else:
            return HttpResponseNotAllowed(['POST'])

    return HttpResponseRedirect(reverse('view:index'))


@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id == post.user_id:
        post.delete()

    return HttpResponseRedirect(reverse('view:index'))


@login_required
def calendar(request):
    template = loader.get_template('view/calendar.html')
    context = {
        'title': 'Eddybeans - Calendar',
    }
    return HttpResponse(template.render(context, request))

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('view:index'))
