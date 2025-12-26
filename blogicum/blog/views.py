from django.utils import timezone

from blog.models import Post, Category
from django.contrib.auth import get_user_model
from django.views.generic import DetailView, CreateView, ListView
from django.core.paginator import Paginator

from django.shortcuts import get_object_or_404, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy

from .forms import UserUpdateForm, PostForm

User = get_user_model()

class PostsListView(ListView):
    model = Post
    template_name = 'blog/index.html'
    paginate_by = 10
    queryset = Post.objects.select_related(
        'author',
        'category',
        'location'
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    )


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

class ProfileView(DetailView):
    """Отображение профиля пользователя с его публикациями."""
    model = User
    template_name = 'blog/profile.html'
    context_object_name = 'profile'
    slug_field = 'username'
    slug_url_kwarg = 'username'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем посты пользователя
        posts = Post.objects.filter(
            author=self.object,
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).select_related('category', 'location', 'author')

        # Пагинация
        paginator = Paginator(posts, 10)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['page_obj'] = page_obj
        return context


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование профиля пользователя."""
    model = User
    form_class = UserUpdateForm
    template_name = 'blog/user.html'

    def get_object(self, queryset=None):
        # Возвращаем текущего пользователя
        return self.request.user

    def get_success_url(self):
        # После успешного редактирования возвращаем на профиль
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание новой публикации."""
    model = Post
    form_class = PostForm
    template_name = 'blog/detailw.html'
    success_url = reverse_lazy('blog:index')  # или другая страница

    def form_valid(self, form):
        """Добавляем автора перед сохранением."""
        form.instance.author = self.request.user

        # Если дата публикации не указана, ставим текущую
        if not form.instance.pub_date:
            form.instance.pub_date = timezone.now()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Добавляем дополнительные данные в контекст."""
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создание новой публикации'
        return context