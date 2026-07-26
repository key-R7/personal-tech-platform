import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.core.paginator import Paginator
from django.db.models import (
    BooleanField,
    Count,
    Exists,
    OuterRef,
    Prefetch,
    Q,
    Value,
)
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import CirclePostForm, SocialCommentForm
from .models import SocialComment, SocialLike, SocialPost

logger = logging.getLogger(__name__)


def social_feed_queryset(request, feed_type):
    """Build the feed without per-post author, comment or like queries."""
    feed_filter = Q(feed_type=feed_type)
    if feed_type == SocialPost.FeedType.CIRCLE:
        feed_filter |= Q(feed_type=SocialPost.FeedType.PERSONAL)

    posts = (
        SocialPost.objects.filter(feed_filter)
        .select_related("author")
        .prefetch_related(
            Prefetch(
                "comments",
                queryset=SocialComment.objects.select_related("author").order_by(
                    "created_at", "pk"
                ),
            )
        )
        .annotate(
            like_count=Count("likes", distinct=True),
            comment_count=Count("comments", distinct=True),
        )
        .order_by("-created_at", "-pk")
    )
    if request.user.is_authenticated:
        return posts.annotate(
            user_has_liked=Exists(
                SocialLike.objects.filter(
                    post=OuterRef("pk"),
                    user=request.user,
                )
            )
        )
    return posts.annotate(
        user_has_liked=Value(False, output_field=BooleanField())
    )


def render_feed(request, feed_type, *, post_form=None, status=200):
    posts = social_feed_queryset(request, feed_type)
    page_obj = Paginator(posts, 10).get_page(request.GET.get("page"))
    context = {
        "feed_type": feed_type,
        "page_obj": page_obj,
        "posts": page_obj.object_list,
        "post_form": post_form,
        "comment_form": SocialCommentForm(),
    }
    return render(request, "social/feed.html", context, status=status)


def personal_feed(request):
    return render_feed(request, SocialPost.FeedType.PERSONAL)


def circle_feed(request):
    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        form = CirclePostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.feed_type = SocialPost.FeedType.CIRCLE
            post.full_clean()
            post.save()
            messages.success(request, "动态发布成功。")
            return redirect("social:circle_feed")
        return render_feed(
            request,
            SocialPost.FeedType.CIRCLE,
            post_form=form,
            status=400,
        )

    post_form = CirclePostForm() if request.user.is_authenticated else None
    return render_feed(
        request,
        SocialPost.FeedType.CIRCLE,
        post_form=post_form,
    )


@login_required
@require_POST
def comment_create(request, post_id):
    post = get_object_or_404(SocialPost, pk=post_id)
    form = SocialCommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.full_clean()
        comment.save()
        messages.success(request, "评论发表成功。")
    else:
        messages.error(request, "评论不能为空且不能超过500字。")
    return redirect(post.get_feed_url())


@login_required
@require_POST
def like_toggle(request, post_id):
    post = get_object_or_404(SocialPost, pk=post_id)
    like, created = SocialLike.objects.get_or_create(
        post=post,
        user=request.user,
    )
    if not created:
        like.delete()
    return redirect(post.get_feed_url())


@login_required
@require_http_methods(["GET", "POST"])
def post_delete(request, post_id):
    post = get_object_or_404(
        SocialPost.objects.select_related("author"),
        pk=post_id,
    )
    if request.user != post.author and not request.user.is_staff:
        logger.warning(
            "User %s attempted to delete social post %s owned by user %s",
            request.user.pk,
            post.pk,
            post.author_id,
        )
        return HttpResponseForbidden("你没有权限删除这条动态。")

    if request.method == "GET":
        return render(
            request,
            "social/post_confirm_delete.html",
            {"post": post},
        )

    redirect_url = post.get_feed_url()
    post.delete()
    messages.success(request, "动态已删除。")
    return redirect(redirect_url)


@login_required
@require_POST
def comment_delete(request, comment_id):
    comment = get_object_or_404(
        SocialComment.objects.select_related("post", "author"),
        pk=comment_id,
    )
    if request.user != comment.author and not request.user.is_staff:
        logger.warning(
            "User %s attempted to delete social comment %s owned by user %s",
            request.user.pk,
            comment.pk,
            comment.author_id,
        )
        return HttpResponseForbidden("你没有权限删除这条评论。")

    redirect_url = comment.post.get_feed_url()
    comment.delete()
    messages.success(request, "评论已删除。")
    return redirect(redirect_url)
