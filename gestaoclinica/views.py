from django.shortcuts import render

# Create your views here.
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm, ConsultaForm, PacienteForm, MedicoForm
from django.contrib import messages
from .models import Paciente, Consulta, Medico
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from django.db.models import Max, F



def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        username_or_email = request.POST['username_or_email']
        password = request.POST['password']
        user = authenticate(request, username=username_or_email, password=password)

        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, 'Credenciais inválidas. Verifique seu email/usuário e senha.')

    return render(request, 'login.html')

@login_required(login_url='nao_autorizado')
def logout_view(request):
    system_messages = messages.get_messages(request)
    for message in system_messages:
        pass
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def inicio(request, medico_id=None):
    # Obtém a data atual
    selected_date = datetime.now().date()

    # Filtra as consultas agendadas para a data atual
    # Se o medico_id for fornecido, filtra por médico
    if medico_id is not None:
        appointments = Consulta.objects.filter(data=selected_date, is_active=True, paciente__is_active=True, compareceu=False, medico_id=medico_id).order_by('data')
        pacientes_compareceram = Consulta.objects.filter(data=selected_date, compareceu=True, medico_id=medico_id).order_by('ordem_comparecimento').distinct()
    else:
        appointments = Consulta.objects.filter(data=selected_date, is_active=True, paciente__is_active=True, compareceu=False)
        pacientes_compareceram = Consulta.objects.filter(data=selected_date, compareceu=True, is_active=True, paciente__is_active=True).order_by('ordem_comparecimento').distinct()


    # Lista de todos os médicos para seleção
    medicos = Medico.objects.filter(is_active=True)

    # Adicione essas informações ao contexto
    context = {
        'selected_date': selected_date,
        'appointments': appointments,
        'active': 'inicio',
        'username': request.user.username,
        'pacientes_compareceram': pacientes_compareceram,
        'medicos': medicos,
        'medico_id_selecionado': int(medico_id) if medico_id is not None else None,  # Para manter o médico selecionado no template
    }

    return render(request, 'inicio.html', context)

def marcar_compareceu(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    
    if not consulta.compareceu:
        # Obtenha a maior ordem de comparecimento atual para o médico específico
        max_ordem_comparecimento = Consulta.objects.filter(
            compareceu=True,
            data__day=date.today().day,    # Filtro para o dia
            data__month=date.today().month,  # Filtro para o mês
            data__year=date.today().year    # Filtro para o ano
        ).aggregate(Max('ordem_comparecimento'))['ordem_comparecimento__max']
        
        # Se não houver consultas com comparecimento para o médico, defina a nova ordem como 1
        nova_ordem = (max_ordem_comparecimento + 1) if max_ordem_comparecimento is not None else 1
        
        # Atualize a ordem de comparecimento da consulta
        consulta.compareceu = True
        consulta.ordem_comparecimento = nova_ordem
        consulta.save()
    else:
        # Reset a ordem de comparecimento e marque como não compareceu
        consulta.compareceu = False
        consulta.ordem_comparecimento = 0
        consulta.save()
    
    return redirect('inicio')
    
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
    else:
        form = CustomUserCreationForm()
    return render(request, 'nova_conta.html', {'form': form})

@login_required(login_url='nao_autorizado')
def gerenciar_pacientes(request):
    pacientes = Paciente.objects.filter(is_active=True)
    context = {'pacientes': pacientes, 'active': 'gerenciarpacientes', 'username': request.user.username}
    return render(request, 'gerenciar_pacientes.html', context)

@login_required(login_url='nao_autorizado')
def prontuario(request, paciente_id):
    paciente = Paciente.objects.get(id=paciente_id)
    observacoes = ObservacaoConsulta.objects.filter(paciente=paciente)
    context = {'paciente': paciente, 'observacoes': observacoes, 'username': request.user.username}
    return render(request, 'prontuario.html', context)

@login_required(login_url='nao_autorizado')
def gerenciar_consultas(request):
    consultas = Consulta.objects.filter(paciente__is_active=True, is_active=True).order_by('data')
    context = {'consultas': consultas, 'active': 'gerenciarconsultas', 'username': request.user.username}
    return render(request, 'gerenciar_consultas.html', context)

@login_required(login_url='nao_autorizado')
def descricao_consulta(request, consulta_id):
    consulta = Consulta.objects.get(id=consulta_id)
    context = {'consulta': consulta, 'username': request.user.username}
    return render(request, 'descricao_consulta.html', context)

@login_required(login_url='nao_autorizado')
def agendar_consulta(request):
    username = request.user.username

    paciente_encontrado = None
    busca_realizada = False
    mostrar_erro = False

    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        cpf = request.POST.get('cpf')

        try:
            paciente_encontrado = Paciente.objects.get(cpf=cpf)
            busca_realizada = True
        except Paciente.DoesNotExist:
            paciente_encontrado = None
            mostrar_erro = True
            messages.error(request, 'Paciente não encontrado com o CPF inserido.')

        if form.is_valid() and paciente_encontrado:
            consulta = form.save(commit=False)
            consulta.paciente = paciente_encontrado

            # Verifique se os campos de convênio e número de carteira foram fornecidos no formulário
            convenio = request.POST.get('convenio')
            num_carteira = request.POST.get('num_carteira')

            if convenio:
                paciente_encontrado.convenio_medico = convenio

            if num_carteira:
                paciente_encontrado.numero_carteira = num_carteira

            paciente_encontrado.save()  # Salve as alterações nos dados do paciente

            consulta.save()
            
            messages.success(request, 'Consulta agendada com sucesso!')
            return redirect('gerenciar_consultas')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = ConsultaForm()

    # Adicione esta parte para buscar todos os médicos no contexto
    medicos = Medico.objects.filter(is_active=True)

    context = {
        'form': form,
        'active': 'novaconsulta',
        'username': username,
        'paciente_encontrado': paciente_encontrado,
        'busca_realizada': busca_realizada,
        'mostrar_erro': mostrar_erro,
        'medicos': medicos,  # Adicione a lista de médicos ao contexto
    }
    return render(request, 'nova_consulta.html', context)

def nao_autorizado(request):
    return render(request, 'nao_autorizado.html')

@login_required(login_url='nao_autorizado')
def editar_consulta(request, consulta_id):
    username = request.user.username
    consulta = get_object_or_404(Consulta, id=consulta_id)
    
    if request.method == 'POST':
        form = ConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()

            convenio = request.POST.get('convenio')
            num_carteira = request.POST.get('num_carteira')

            if convenio:
                consulta.paciente.convenio_medico = convenio

            if num_carteira:
                consulta.paciente.numero_carteira = num_carteira

            consulta.paciente.save()  # Salve as alterações nos dados do paciente

            return redirect('gerenciar_consultas')
    else:
        # Exclua o campo 'descricao' do formulário
        form = ConsultaForm(instance=consulta)
        form.fields.pop('descricao')
    
    context = {'form': form, 'consulta': consulta, 'active': 'gerenciarconsultas', 'username': username}
    return render(request, 'editar_consulta.html', context)

@login_required(login_url='nao_autorizado')
def editar_descricao_consulta(request, consulta_id):
    username = request.user.username
    consulta = get_object_or_404(Consulta, id=consulta_id)

    if request.method == 'POST':
        # Crie um formulário apenas com o campo de descrição
        form = ConsultaForm(request.POST, instance=consulta)
        form.fields = {'descricao': form.fields['descricao']}  # Mantenha apenas o campo 'descricao'
        
        if form.is_valid():
            form.save()
            return redirect('gerenciar_consultas')
    else:
        # Crie um formulário apenas com o campo de descrição
        form = ConsultaForm(instance=consulta)
        form.fields = {'descricao': form.fields['descricao']}  # Mantenha apenas o campo 'descricao'

    context = {'form': form, 'consulta': consulta, 'active': 'gerenciarconsultas', 'username': username}
    return render(request, 'editar_descricao_consulta.html', context)

@login_required(login_url='nao_autorizado')
def excluir_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, id=consulta_id)
    consulta.is_active = False
    consulta.save()
    return redirect('gerenciar_consultas')


@login_required(login_url='nao_autorizado')
def cadastrar_paciente(request):
    username = request.user.username
    cpf_existente = False

    if request.method == 'POST':
        form = PacienteForm(request.POST)
        cpf = request.POST.get('cpf')

        # Verifique se o CPF já existe no banco de dados
        if Paciente.objects.filter(cpf=cpf).exists():
            cpf_existente = True
            messages.error(request, 'Paciente com o CPF inserido já está cadastrado no sistema.')
        else:
            if form.is_valid():
                form.save()
                messages.success(request, 'Paciente cadastrado com sucesso.')
                return redirect('gerenciar_pacientes')
    
    else:
        form = PacienteForm()
    
    context = {
        'form': form,
        'active': 'gerenciarpacientes',
        'username': username,
        'cpf_existente': cpf_existente,
    }
    return render(request, 'novo_paciente.html', context)

@login_required(login_url='nao_autorizado')
def editar_paciente(request, paciente_id):
    username = request.user.username
    # Recupere o paciente que você deseja editar ou retorne um erro 404 se não for encontrado
    paciente = get_object_or_404(Paciente, id=paciente_id)

    if request.method == 'POST':
        # Preencha o formulário com os dados do paciente existente
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            form.save()
            return redirect('gerenciar_pacientes')  # Redirecionar para a página de gerenciamento de pacientes após a edição
    else:
        # Preencha o formulário com os dados do paciente existente
        form = PacienteForm(instance=paciente)
    
    context = {'form': form, 'paciente': paciente, 'active': 'gerenciarpacientes', 'username': username}
    return render(request, 'editar_paciente.html', context)


@login_required(login_url='nao_autorizado')
def excluir_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    paciente.is_active = False
    paciente.save()
    return redirect('gerenciar_pacientes')




@login_required(login_url='nao_autorizado')
def gerenciar_medicos(request):
    medicos = Medico.objects.filter(is_active=True)
    context = {'medicos': medicos, 'active': 'gerenciarmedicos', 'username': request.user.username}
    return render(request, 'gerenciar_medicos.html', context)

@login_required(login_url='nao_autorizado')
def novo_medico(request):
    username = request.user.username

    medico_encontrado = None
    mostrar_erro = False

    if request.method == 'POST':
        form = MedicoForm(request.POST)
        crm = request.POST.get('crm')

        try:
            medico_encontrado = Medico.objects.get(crm=crm)
            mostrar_erro = True  # Set this flag if the doctor with the given CRM is found
            messages.error(request, 'Médico com o CRM inserido já está cadastrado no sistema.')
        except Medico.DoesNotExist:
            medico_encontrado = None

        if form.is_valid() and not medico_encontrado:
            form.save()
            messages.success(request, 'Médico adicionado com sucesso.')
            return redirect('gerenciar_medicos')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = MedicoForm()

    context = {
        'form': form,
        'active': 'gerenciarmedicos',
        'username': username,
        'mostrar_erro': mostrar_erro,
    }
    return render(request, 'novo_medico.html', context)


@login_required(login_url='nao_autorizado')
def editar_medico(request, medico_id):
    # Recupere o médico que você deseja editar ou retorne um erro 404 se não for encontrado
    medico = get_object_or_404(Medico, id=medico_id)

    if request.method == 'POST':
        # Preencha o formulário com os dados do médico existente
        form = MedicoForm(request.POST, instance=medico)
        if form.is_valid():
            form.save()
            return redirect('gerenciar_medicos')  # Redirecionar para a página de gerenciamento de médicos após a edição
    else:
        # Preencha o formulário com os dados do médico existente
        form = MedicoForm(instance=medico)
    
    context = {'form': form, 'medico': medico, 'active': 'gerenciarmedicos', 'username': request.user.username,}
    return render(request, 'editar_medico.html', context)

# View para excluir um médico específico
@login_required(login_url='nao_autorizado')
def excluir_medico(request, medico_id):
    medico = get_object_or_404(Medico, id=medico_id)
    medico.is_active = False
    medico.save()  # Salve as alterações no objeto médico
    return redirect('gerenciar_medicos')



@login_required(login_url='nao_autorizado')
def prontuario_paciente(request, paciente_id):
    paciente = get_object_or_404(Paciente, id=paciente_id)
    consultas = Consulta.objects.filter(paciente=paciente).order_by('data')
    
    # Calcula a idade atual do paciente
    hoje = date.today()
    idade = hoje.year - paciente.data_nascimento.year - ((hoje.month, hoje.day) < (paciente.data_nascimento.month, paciente.data_nascimento.day))
    
    context = {
        'paciente': paciente,
        'consultas': consultas,
        'idade': idade,
        'active': 'gerenciarpacientes',
        'username': request.user.username
    }
    
    return render(request, 'prontuario_paciente.html', context)