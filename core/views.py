from django.shortcuts import redirect, render
from django.templatetags.static import static

from blog.models import Article
from projects.models import Project

from .content import about_page_content, home_page_content


def home(request):
    """Render the homepage with recent articles and featured projects."""
    context = {
        "recent_articles": Article.objects.public().order_by(
            "-published_at", "-created_at"
        )[:3],
        "featured_projects": Project.objects.filter(featured=True)
        .order_by("-updated_at", "-created_at")[:3],
        "home_content": home_page_content(),
    }
    return render(request, "core/home.html", context)


def about(request):
    """Render the About page with Admin-managed content or safe fallbacks."""
    return render(
        request,
        "core/about.html",
        {"about_content": about_page_content()},
    )


def favicon(request):
    """Redirect the conventional browser favicon URL to the static icon."""
    return redirect(static("favicon.svg"), permanent=True)
