from django.shortcuts import render
from django.conf import settings
import locale
from dashboard.services import Covid
from dashboard.services import VacinasGerais

def index(request):
    return render(request, 'index.html')

def covid(request):

    locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' ) 

    covid = Covid()
    
    covid_dados_gerais = covid.covid_dados()
   
    covid_dados_gerais_por_estado = covid.covid_dados_por_estado()

    covid_dados_vacinacao = covid.covid_vacinacao()

    return render(request, 'covid.html', {'covid_confirmed_cases': covid_dados_gerais[0], 'covid_recovered_cases': covid_dados_gerais[1], 'covid_death_cases': covid_dados_gerais[2], 
        'covid_report_date': covid_dados_gerais[3], 'lista_covid_dados': covid_dados_gerais[4], 'covid_vac_doses_totais': covid_dados_vacinacao[0], 'covid_vac_primeira_dose': covid_dados_vacinacao[1], 
            'covid_vac_segunda_dose': covid_dados_vacinacao[2], 'covid_vac_doses_reforco': covid_dados_vacinacao[3], 
                'covid_vac_data_atualizacao': covid_dados_vacinacao[4], 'lista_vac_dados': covid_dados_vacinacao[5], 'lista_vac_labels': covid_dados_vacinacao[6], 'lista_vac_taxas': covid_dados_vacinacao[7], 'covid_data_per_state': covid_dados_gerais_por_estado[0], 'ufs': covid_dados_gerais_por_estado[1],
                     'cases': covid_dados_gerais_por_estado[2], 'deaths': covid_dados_gerais_por_estado[3]})

def vacinas(request):
    vacinas = VacinasGerais()
    df_vacinas_gerais = vacinas.vacina_dados_gerais()
    dados_vacinas_regiao = vacinas.vacina_dados_gerais_por_regiao()
    dados_vacinas_ano = vacinas.vacina_dados_gerais_por_ano()
    return render(request, 'vacinas.html',{'df': df_vacinas_gerais, 'labels_regiao': dados_vacinas_regiao[0], 'lista': dados_vacinas_regiao[1], 'labels_ano': dados_vacinas_ano[0], 'lista_ano': dados_vacinas_ano[1]})

def projeto(request):
    return render(request, 'projeto.html')