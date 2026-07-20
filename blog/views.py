import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import CommentForm
from .models import Article, Category, Comment, Tag

logger = logging.getLogger(__name__)


def published_articles():
    """Compatibility helper for code that needs the public article queryset."""
    return Article.objects.public()


def article_list(request):
    articles = (
        Article.objects.public()
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-published_at", "-created_at")
    )

    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    tag_slug = request.GET.get("tag", "").strip()
    current_category = None
    current_tag = None

    if category_slug:
        current_category = get_object_or_404(Category, slug=category_slug)
        articles = articles.filter(category=current_category)

    if tag_slug:
        current_tag = get_object_or_404(Tag, slug=tag_slug)
        articles = articles.filter(tags=current_tag)

    if query:
        articles = articles.filter(
            Q(title__icontains=query) | Q(summary__icontains=query)
        )

    paginator = Paginator(articles.distinct(), 5)
    page_obj = paginator.get_page(request.GET.get("page"))
    pagination_parameters = request.GET.copy()
    pagination_parameters.pop("page", None)

    context = {
        "articles": page_obj.object_list,
        "page_obj": page_obj,
        "categories": Category.objects.all(),
        "tags": Tag.objects.all(),
        "current_category": current_category,
        "current_tag": current_tag,
        "query": query,
        "pagination_query": pagination_parameters.urlencode(),
    }
    return render(request, "blog/article_list.html", context)


def article_detail_context(article, comment_form=None):
    return {
        "article": article,
        "comments": article.comments.select_related("author").all(),
        "comment_form": comment_form or CommentForm(),
    }


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.public()
        .select_related("category")
        .prefetch_related("tags"),
        slug=slug,
    )
    return render(
        request,
        "blog/article_detail.html",
        article_detail_context(article),
    )


@login_required
@require_POST
def comment_create(request, slug):
    article = get_object_or_404(Article.objects.public(), slug=slug)
    form = CommentForm(request.POST)

    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.author = request.user
        comment.save()
        messages.success(request, "评论发表成功。")
        return redirect(article)

    return render(
        request,
        "blog/article_detail.html",
        article_detail_context(article, comment_form=form),
        status=400,
    )


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(
        Comment.objects.select_related("article", "author"),
        pk=pk,
    )
    if request.user != comment.author and not request.user.is_staff:
        logger.warning(
            "User %s attempted to delete comment %s owned by user %s",
            request.user.pk,
            comment.pk,
            comment.author_id,
        )
        return HttpResponseForbidden("你没有权限删除这条评论。")

    article = comment.article
    comment.delete()
    messages.success(request, "评论已删除。")
    return redirect(article)
