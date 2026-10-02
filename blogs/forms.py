from django import forms

from .models import BlogPost

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class PostForm(forms.ModelForm):
    files = forms.FileField(
        widget=MultipleFileInput(attrs={
            'multiple': True,
            'class': 'form-control-file'
        }),
        required=False,
        label="Прикрепить файлы (до 10 шт.)"
    )

    class Meta:
        model = BlogPost
        fields = ('title', 'text', 'is_published')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'is_published': forms.CheckboxInput(attrs={'class': 'custom-control-input', "checked": "True"}),
        }

    def clean_files(self):
        files = self.files.getlist('files')
        
        if len(files) > 10:
            raise forms.ValidationError("Вы не можете загрузить более 10 файлов.")
            
        return files