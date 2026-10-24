from django import forms
from django_select2 import forms as s2forms

from .models import BlogPost, Hashtag, Comment

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []

        if isinstance(data, (list, tuple)):
            files = data
        else:
            files = [data]

        cleaned_files = []

        for file in files:
            cleaned_files.append(
                super().clean(file, initial)
            )

        if len(cleaned_files) > 10:
            raise forms.ValidationError(
                "Вы не можете загрузить более 10 файлов."
            )

        return cleaned_files

class HashtagAutocompleteWidget(s2forms.ModelSelect2MultipleWidget):
    model = Hashtag
    search_fields = [
        'text__icontains',
    ]

class PostForm(forms.ModelForm):
    files = MultipleFileField(
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'class': 'form-control-file'
        }),
        required=False,
        label="Прикрепить файлы (до 10 шт.)"
    )

    class Meta:
        model = BlogPost
        fields = ('title', 'text', 'hashtags', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'hashtags': HashtagAutocompleteWidget(attrs={
                'class': 'form-control',
                'data-placeholder': 'Начните вводить хэштег...',
                'data-minimum-input-length': 1,
            }),
            'is_published': forms.CheckboxInput(attrs={'class': 'custom-control-input', "checked": "True"}),
        }
    

    def clean_files(self):
        files = self.files.getlist('files')
        
        if len(files) > 10:
            raise forms.ValidationError("Вы не можете загрузить более 10 файлов.")
            
        return files
    
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'Напишите комментарий...', 
                'rows': 3
            })
        }