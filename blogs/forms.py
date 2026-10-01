from django import forms

from .models import BlogPost

class PostForm(forms.ModelForm):
    files = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'multiple': True,
            'class': 'form-control-file'
        }),
        required=False,
        label="Прикрепить файлы (до 10 шт.)"
    )

    class Meta:
        model = BlogPost
        fields = ('title', 'content')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
        }

    def clean_files(self):
        files = self.files.getlist('files')
        
        if len(files) > 10:
            raise forms.ValidationError("Вы не можете загрузить более 10 файлов.")
            
        return files