from django import forms



class LoginForm(forms.Form):

    usuario = forms.CharField(
        required=True,
        label = 'Usuario',
        widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder' : 'Usuario...'
        }),
        help_text="Nombre de usuario para iniciar sesion"
    )

    password = forms.CharField(
        required=True,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class' : 'form-control',
            'placeholder' : 'Contraseña...'
        }),
        help_text="Contraseña de usuario"
    )
