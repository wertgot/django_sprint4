from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from blog.models import Post, Category


def index(request):
    template = "blog/index.html"
    post_list = Post.objects.select_related(
        'author',
        'category',
        'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )[:5]

    context = {
        "post_list": post_list,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "blog/detail.html"

    post = get_object_or_404(
        Post.objects.select_related(
            'author',
            'category',
            'location'
        ),
        id=post_id,

        pub_date__lte=timezone.now(),
        is_published=True,
        category__is_published=True
    )

    context = {'post': post}
    return render(request, template, context)


def category_posts(request, category_slug):
    template = "blog/category.html"

    category = get_object_or_404(
        Category.objects.all(),
        slug=category_slug,
        is_published=True
    )

    post_list = category.posts.select_related(
        'author',
        'category',
        'location'
    ).filter(
        is_published=True,
        pub_date__lte=timezone.now()
    )

    context = {
        'post_list': post_list,
        'category': category
    }
    return render(request, template, context)
