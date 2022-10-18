from django.forms import ModelForm
from .models import Post, Comment


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': 'Введите текст поста',
            'group': 'Выберите группу'
        }
        help_texts = {
            'text': 'Текст поста',
            'group': 'Группа поста'
        }


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
