from django.conf import settings
from datetime import datetime, timedelta
from dashboard.models import CovidDados, CovidDadosVacinacao
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
import requests
import pandas as pd
import locale

class Covid():

    def covid_dados(self):
        locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
        ultimo_registro_db = CovidDados.objects.last()
        if(ultimo_registro_db is not None and ultimo_registro_db.data.date() == datetime.today().date() - timedelta(days=1)):
            covid_confirmed_cases = ultimo_registro_db.casos_confirmados
            covid_recovered_cases = ultimo_registro_db.casos_recuperados
            covid_death_cases =  ultimo_registro_db.mortes
            covid_report_date = datetime.fromisoformat(str(ultimo_registro_db.data)).strftime('%d-%m-%Y')
        else:
            covid_url = requests.get(settings.URL_DADOS_COVID19_GERAL)
            all_covid_data_status = covid_url.status_code
            if all_covid_data_status == 200:        
                try:
                    all_covid_data = covid_url.json()
                    latest_covid_data = all_covid_data[len(all_covid_data) - 1]
                    covid_confirmed_cases = '{:,}'.format(latest_covid_data['Confirmed'])
                    covid_recovered_cases = '{:,}'.format(latest_covid_data['Active'])
                    covid_death_cases = '{:,}'.format(latest_covid_data['Deaths'])
                    covid_report_datetime = latest_covid_data['Date']
                    covid_report_date = datetime.fromisoformat(latest_covid_data['Date'][0:10]).strftime('%d-%m-%Y')
                    covid_dados_db = CovidDados.objects.create(casos_confirmados = covid_confirmed_cases, casos_recuperados = covid_recovered_cases, mortes = covid_death_cases, data = covid_report_datetime)
                    covid_dados_db.save
                except:
                    pass
                    print('Erro consulta dos dados da Covid-19 no Brasil!')

        taxa_mortalidade = round((float(covid_death_cases.strip().replace(',',''))/float(covid_confirmed_cases.strip().replace(',','')))*100.0, 2)
        taxa_casos_recuperados = round((float(covid_recovered_cases.strip().replace(',',''))/float(covid_confirmed_cases.strip().replace(',','')))*100.0, 2)
        lista_covid_taxas = [taxa_mortalidade, taxa_casos_recuperados]

        return covid_confirmed_cases, covid_recovered_cases, covid_death_cases, covid_report_date, lista_covid_taxas

    def covid_dados_por_estado(self):
            ufs = []
            cases = []
            deaths = []
            covid_state_url = requests.get(settings.URL_DADOS_COVID19_POR_ESTADO)
            covid_state_url_status = covid_state_url.status_code
            if covid_state_url_status == 200:
                try:
                    covid_state_data = covid_state_url.json()
                    data_per_state = covid_state_data['data']
                    for item in data_per_state:
                        ufs.append(item['uf'])
                        cases.append(item['cases'])
                        deaths.append(item['deaths'])
                except:
                    pass
                    print('Erro consulta dos dados da Covid-19 no Brasil por estado')
            return data_per_state, ufs, cases, deaths

    def covid_vacinacao(self):
        locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
        ultimo_registro_db = CovidDadosVacinacao.objects.last()
        if(ultimo_registro_db is not None and ultimo_registro_db.dados_vacinacao_data_atualizacao == datetime.today().date() - timedelta(days=1)):
            dados_vacinacao_total_doses = ultimo_registro_db.dados_vacinacao_total_doses
            dados_vacinacao_primeira_dose = ultimo_registro_db.dados_vacinacao_primeira_dose
            dados_vacinacao_segunda_e_unica_dose =  ultimo_registro_db.dados_vacinacao_segunda_e_unica_dose
            dados_vacinacao_dose_reforco = ultimo_registro_db.dados_vacinacao_dose_reforco
            dados_vacinacao_data_atualizacao = ultimo_registro_db.dados_vacinacao_data_atualizacao.strftime('%d-%m-%Y')
        else:
            try:
                dados_vacinacao_url = settings.URL_DADOS_COVID19_VACINACAO
                df = pd.read_csv(dados_vacinacao_url)
                dados_vacinacao = df.loc[df['state'] == 'TOTAL']
                dados_vacinacao_primeira_dose = '{:,}'.format(dados_vacinacao['vaccinated'].values[0])
                dados_vacinacao_segunda_dose = '{:,}'.format(dados_vacinacao['vaccinated_second'].values[0])
                dados_vacinacao_unica_dose = '{:,}'.format(dados_vacinacao['vaccinated_single'].values[0])
                dados_vacinacao_dose_reforco = '{:,}'.format(dados_vacinacao['vaccinated_third'].values[0])
                dados_vacinacao_data_atualizacao = datetime.fromisoformat(dados_vacinacao['date'].values[0]).strftime('%Y-%m-%d')
                        
                dados_vacinacao_segunda_e_unica_dose = 	locale.atoi(dados_vacinacao_segunda_dose) + locale.atoi(dados_vacinacao_unica_dose)
                dados_vacinacao_total_doses = locale.atoi(dados_vacinacao_primeira_dose) + (dados_vacinacao_segunda_e_unica_dose) + locale.atoi(dados_vacinacao_dose_reforco)

                dados_vacinacao_segunda_e_unica_dose = '{:,}'.format(dados_vacinacao_segunda_e_unica_dose)
                dados_vacinacao_total_doses = '{:,}'.format(dados_vacinacao_total_doses)

                covid_dados_vacinacao_db = CovidDadosVacinacao.objects.create(dados_vacinacao_total_doses = dados_vacinacao_total_doses, dados_vacinacao_primeira_dose = dados_vacinacao_primeira_dose, dados_vacinacao_segunda_e_unica_dose = dados_vacinacao_segunda_e_unica_dose, dados_vacinacao_dose_reforco = dados_vacinacao_dose_reforco, dados_vacinacao_data_atualizacao = dados_vacinacao_data_atualizacao)
                covid_dados_vacinacao_db.save
            except:
                print('Erro na consulta dos dados da vacinação no Brasil!')

        taxa_vacinacao_primeira_dose = round(float(dados_vacinacao_primeira_dose.strip().replace(',',''))/215000000*100.0, 2)
        taxa_vacinacao_segunda_e_unica_dose = round(float(dados_vacinacao_segunda_e_unica_dose.strip().replace(',',''))/215000000*100.0, 2)
        taxa_vacinacao_dose_reforco = round(float(dados_vacinacao_dose_reforco.strip().replace(',',''))/215000000*100.0, 2)

        lista_dados = [int(dados_vacinacao_primeira_dose.replace(',','')), int(dados_vacinacao_segunda_e_unica_dose.replace(',','')), int(dados_vacinacao_dose_reforco.replace(',',''))]
        lista_labels = ['Primeira dose', 'Segunda dose e unica dose', 'Dose de reforço']
        lista_taxas_vacinacao = [taxa_vacinacao_primeira_dose, taxa_vacinacao_segunda_e_unica_dose, taxa_vacinacao_dose_reforco]
        return dados_vacinacao_total_doses, dados_vacinacao_primeira_dose, dados_vacinacao_segunda_e_unica_dose, dados_vacinacao_dose_reforco, dados_vacinacao_data_atualizacao, lista_dados, lista_labels, lista_taxas_vacinacao

class VacinasGerais():
    def vacina_dados_gerais(self):
        dados_vacinas_path = settings.CSV_DADOS_VACINAS
        try:
            df = pd.read_csv(dados_vacinas_path, delimiter=';')
        except:
            print('Erro na consulta dos dados das vacinas no Brasil!')
        
        return df
    
    def vacina_dados_gerais_por_regiao(self):
        dados_vacinas_path = settings.CSV_DADOS_VACINAS
        bcg = []
        febre_amarela = []
        hepatite_a = []
        hepatite_b = []
        varicela = []
        poliomelite = []
        mncc = []
        vorh = []
        penta = []
        pneumococica = []
        tetraviral = []
        lista_dados_vacinas = []
        try:
            df = pd.read_csv(dados_vacinas_path, delimiter=';')
            df = df.groupby(['Região']).sum()/5
            labels_regioes = ['Centro-Oeste','Nordeste','Norte','Sudeste','Sul']
            dataList = df.iloc[:, 0].tolist()
            for data in dataList:
                bcg.append(round(float(data),2))
            dataList = df.iloc[:, 1].tolist()
            for data in dataList:
                febre_amarela.append(round(float(data),2))
            dataList = df.iloc[:, 2].tolist()
            for data in dataList:
                hepatite_a.append(round(float(data),2))
            dataList = df.iloc[:, 3].tolist()
            for data in dataList:
                hepatite_b.append(round(float(data),2))
            dataList = df.iloc[:, 4].tolist()
            for data in dataList:
                varicela.append(round(float(data),2))
            dataList = df.iloc[:, 5].tolist()
            for data in dataList:
                poliomelite.append(round(float(data),2))
            dataList = df.iloc[:, 6].tolist()
            for data in dataList:
                mncc.append(round(float(data),2))
            dataList = df.iloc[:, 7].tolist()
            for data in dataList:
                vorh.append(round(float(data),2))
            dataList = df.iloc[:, 8].tolist()
            for data in dataList:
                penta.append(round(float(data),2))
            dataList = df.iloc[:, 9].tolist()
            for data in dataList:
                pneumococica.append(round(float(data),2))
            dataList = df.iloc[:, 10].tolist()
            for data in dataList:
                tetraviral.append(round(float(data),2))
            lista_dados_vacinas = [bcg, febre_amarela, hepatite_a, hepatite_b, varicela, poliomelite, mncc, vorh, penta, pneumococica, tetraviral]
        except:
            print('Erro na consulta dos dados das vacinas no Brasil!')
        
        return labels_regioes, lista_dados_vacinas
    
    def vacina_dados_gerais_por_ano(self):
        dados_vacinas_path = settings.CSV_DADOS_VACINAS
        bcg = []
        febre_amarela = []
        hepatite_a = []
        hepatite_b = []
        varicela = []
        poliomelite = []
        mncc = []
        vorh = []
        penta = []
        pneumococica = []
        tetraviral = []
        lista_dados_vacinas = []
        try:
            df = pd.read_csv(dados_vacinas_path, delimiter=';')
            df = df.groupby(['Ano']).sum()/5
            labels_ano = ['2018', '2019', '2020', '2021', '2022']
            dataList = df.iloc[:, 0].tolist()
            for data in dataList:
                bcg.append(round(float(data),2))
            dataList = df.iloc[:, 1].tolist()
            for data in dataList:
                febre_amarela.append(round(float(data),2))
            dataList = df.iloc[:, 2].tolist()
            for data in dataList:
                hepatite_a.append(round(float(data),2))
            dataList = df.iloc[:, 3].tolist()
            for data in dataList:
                hepatite_b.append(round(float(data),2))
            dataList = df.iloc[:, 4].tolist()
            for data in dataList:
                varicela.append(round(float(data),2))
            dataList = df.iloc[:, 5].tolist()
            for data in dataList:
                poliomelite.append(round(float(data),2))
            dataList = df.iloc[:, 6].tolist()
            for data in dataList:
                mncc.append(round(float(data),2))
            dataList = df.iloc[:, 7].tolist()
            for data in dataList:
                vorh.append(round(float(data),2))
            dataList = df.iloc[:, 8].tolist()
            for data in dataList:
                penta.append(round(float(data),2))
            dataList = df.iloc[:, 9].tolist()
            for data in dataList:
                pneumococica.append(round(float(data),2))
            dataList = df.iloc[:, 10].tolist()
            for data in dataList:
                tetraviral.append(round(float(data),2))
            lista_dados_vacinas = [bcg, febre_amarela, hepatite_a, hepatite_b, varicela, poliomelite, mncc, vorh, penta, pneumococica, tetraviral]
        except:
            print('Erro na consulta dos dados das vacinas no Brasil!')
        
        return labels_ano, lista_dados_vacinas