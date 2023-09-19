from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Consulta, Paciente, Medico

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(max_length=254, required=True, help_text='Insira um email válido para continuar.')
    username = forms.CharField(max_length=30, required=True, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        error_messages = {
            'password_mismatch': 'As senhas não coincidem.',
        }

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['paciente', 'medico', 'data', 'descricao', 'convenio', 'num_carteira']  # Certifique-se de que os campos estão corretos

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        exclude = ['is_active']

class MedicoForm(forms.ModelForm):
    class Meta:
        model = Medico
        fields = ['nome', 'crm']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adicione classes CSS personalizadas, se necessário
        self.fields['nome'].widget.attrs['class'] = 'form-control'
        self.fields['crm'].widget.attrs['class'] = 'form-control'