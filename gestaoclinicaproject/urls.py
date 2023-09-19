from django.urls import path
from gestaoclinica import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('registrar/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:medico_id>/', views.inicio, name='inicio'),
    path('gerenciarpacientes/', views.gerenciar_pacientes, name='gerenciar_pacientes'),
    path('gerenciarpacientes/<int:paciente_id>/', views.prontuario, name='prontuario'),
    path('gerenciarconsultas/', views.gerenciar_consultas, name='gerenciar_consultas'),
    path('gerenciarconsultas/<int:consulta_id>/', views.descricao_consulta, name='descricao_consulta'),
    path('editar_descricao_consulta/<int:consulta_id>/', views.editar_descricao_consulta, name='editar_descricao_consulta'),
    path('novaconsulta/', views.agendar_consulta, name='nova_consulta'),
    path('nao-autorizado/', views.nao_autorizado, name='nao_autorizado'),
    path('novopaciente/', views.cadastrar_paciente, name='novo_paciente'),
    path('editar_paciente/<int:paciente_id>/', views.editar_paciente, name='editar_paciente'),
    path('excluir_paciente/<int:paciente_id>/', views.excluir_paciente, name='excluir_paciente'),
    path('editar_consulta/<int:consulta_id>/', views.editar_consulta, name='editar_consulta'),
    path('excluir_consulta/<int:consulta_id>/', views.excluir_consulta, name='excluir_consulta'),
    path('gerenciarmedicos/', views.gerenciar_medicos, name='gerenciar_medicos'),
    path('medicos/novo/', views.novo_medico, name='novo_medico'),
    path('medicos/editar/<int:medico_id>/', views.editar_medico, name='editar_medico'),
    path('medicos/excluir/<int:medico_id>/', views.excluir_medico, name='excluir_medico'),
    path('prontuario/paciente/<int:paciente_id>/', views.prontuario_paciente, name='prontuario_paciente'),
    path('marcar_compareceu/<int:consulta_id>/', views.marcar_compareceu, name='marcar_compareceu'),

]