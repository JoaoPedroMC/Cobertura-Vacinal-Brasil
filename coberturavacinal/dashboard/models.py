from django.db import models

# Create your models here.

class CovidDados(models.Model):
    casos_confirmados = models.CharField(max_length=100)
    casos_recuperados = models.CharField(max_length=100)
    mortes = models.CharField(max_length=100)
    data = models.DateTimeField()

class CovidDadosVacinacao(models.Model):
    dados_vacinacao_total_doses = models.CharField(max_length=100)
    dados_vacinacao_primeira_dose = models.CharField(max_length=100)
    dados_vacinacao_segunda_e_unica_dose = models.CharField(max_length=100)
    dados_vacinacao_dose_reforco = models.CharField(max_length=100)
    dados_vacinacao_data_atualizacao = models.DateField()