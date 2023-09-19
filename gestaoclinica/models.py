from django.db import models

class Paciente(models.Model):
    nome = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True) 
    cpf = models.CharField(max_length=14, unique=True)
    data_nascimento = models.DateField()
    sexo = models.CharField(max_length=1, blank=True)
    endereco = models.TextField(blank=True)
    convenio_medico = models.CharField(max_length=100, blank=True)
    numero_carteira = models.CharField(max_length=20, blank=True)
    numero_telefone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.nome

class Medico(models.Model):
    is_active = models.BooleanField(default=True) 
    nome = models.CharField(max_length=100)
    crm = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.nome

class Consulta(models.Model):
    is_active = models.BooleanField(default=True) 
    paciente = models.ForeignKey(Paciente, on_delete=models.PROTECT)
    medico = models.ForeignKey(Medico, on_delete=models.PROTECT)
    data = models.DateField()
    descricao = models.TextField(blank=True)
    compareceu = models.BooleanField(default=False)
    ordem_comparecimento = models.PositiveIntegerField(default=0)
    convenio = models.CharField(max_length=100, blank=True)
    num_carteira = models.CharField(max_length=20, blank=True)