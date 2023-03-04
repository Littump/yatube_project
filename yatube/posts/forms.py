from django import forms

from .models import Group, Post


class PostForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['group'].required = False
        self.fields['group'].queryset = Group.objects.all()

    class Meta:
        model = Post
        fields = ('group', 'text',)
        widgets = {'group': forms.Select(attrs={'class': 'form-control'})}
        help_texts = {
            'text': 'Введите текст поста'
        }
