# Atenção: respostas às questões textuais estão nos comentários junto com o código na seção de visualização

import streamlit as st 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import altair as alt
import plotly.express as px
from plotly.subplots import make_subplots
import pydeck as pdk

### Carga dos dados ###
df_covid_parte1 = pd.read_csv("HIST_PAINEL_COVIDBR_2025_Parte1_05set2025.csv", sep=";", encoding="utf-8")
df_covid_parte2 = pd.read_csv("HIST_PAINEL_COVIDBR_2025_Parte2_05set2025.csv", sep=";", encoding="utf-8")

df_covid = pd.concat([df_covid_parte1, df_covid_parte2], ignore_index=True)

### Preparação dos dados ###

# Questão 2 #
# Estado: AM

df_covid_qt2 = df_covid[df_covid['estado'] == 'AM']
df_covid_qt2 = df_covid_qt2[df_covid_qt2['municipio'].isna()][['estado', 'semanaEpi', 'casosNovos']]

# Necessário agregar os casos novos por semana, pois a base de dados registra uma entrada por data
df_agrupado_qt2 = df_covid_qt2.groupby(["semanaEpi"]).agg({
    'estado': 'first',
    'casosNovos': 'sum'
    })

df_agrupado_qt2['semanaEpi'] = df_agrupado_qt2.index
df_agrupado_qt2 = df_agrupado_qt2.reset_index(drop=True)

# Questão 3 #
df_covid_qt3 = df_covid[df_covid['regiao'] == 'Brasil']
df_covid_qt3 = df_covid_qt3[df_covid_qt3['estado'].isna()][['regiao', 'semanaEpi', 'obitosAcumulado']]

#agregação por semana epidemiológica
df_agrupado_qt3 = df_covid_qt3.groupby(["semanaEpi"]).agg({
    'regiao': 'first',
    'obitosAcumulado': 'last'
    })

df_agrupado_qt3['semanaEpi'] = df_agrupado_qt3.index
df_agrupado_qt3 = df_agrupado_qt3.reset_index(drop=True)

# Questão 4 #
estados_qt4 = ['AM', 'RS', 'SP']

df_covid_qt4 = df_covid[df_covid['estado'].isin(estados_qt4)]
df_covid_qt4 = df_covid_qt4[df_covid_qt4['municipio'].isna() & df_covid_qt4['codmun'].isna()][['estado', 'semanaEpi', 'casosAcumulado']]

#agregação por semana epidemiológica
df_agrupado_qt4 = df_covid_qt4.groupby(["semanaEpi", "estado"]).agg({
    'casosAcumulado': 'max'
    })

df_agrupado_qt4['estado'] = [estado[1] for estado in df_agrupado_qt4.index]
df_agrupado_qt4['semanaEpi'] = [semana[0] for semana in df_agrupado_qt4.index]
df_agrupado_qt4 = df_agrupado_qt4[['estado', 'semanaEpi', 'casosAcumulado']].reset_index(drop=True)

casos_AM = df_agrupado_qt4[df_agrupado_qt4['estado'] == 'AM']
casos_AM = casos_AM.rename(columns={'casosAcumulado': 'casosAcumulado_AM'}).drop(columns=['estado'])

casos_RS = df_agrupado_qt4[df_agrupado_qt4['estado'] == 'RS']
casos_RS = casos_RS.rename(columns={'casosAcumulado': 'casosAcumulado_RS'}).drop(columns=['estado'])

casos_SP = df_agrupado_qt4[df_agrupado_qt4['estado'] == 'SP']
casos_SP = casos_SP.rename(columns={'casosAcumulado': 'casosAcumulado_SP'}).drop(columns=['estado'])

df_4_final = casos_AM.merge(casos_RS, on='semanaEpi').merge(casos_SP, on='semanaEpi')

# Questão 5 (mapa com streamlit) #

df_covid_qt5 = df_covid[df_covid['estado'] == 'PE']
df_covid_qt5 = df_covid_qt5.dropna(subset=['municipio'])[['estado', 'municipio', 'semanaEpi', 'casosAcumulado']]

#agregação por semana epidemiológica
df_agrupado_qt5 = df_covid_qt5.groupby(["municipio", "semanaEpi"]).agg({
    'municipio': 'first',
    'estado': 'first',
    'casosAcumulado': 'sum'
    })

df_agrupado_qt5['municipio'] = [mun[0] for mun in df_agrupado_qt5.index]
df_agrupado_qt5['semanaEpi'] = [semana[1] for semana in df_agrupado_qt5.index]
df_agrupado_qt5 = df_agrupado_qt5[['estado', 'municipio', 'semanaEpi', 'casosAcumulado']].reset_index(drop=True)

df_qt5_max = df_agrupado_qt5[df_agrupado_qt5['semanaEpi'] == df_agrupado_qt5['semanaEpi'].max()].sort_values(by='casosAcumulado', ascending=False)

cidades_mais_casos = list(df_qt5_max.head(5)['municipio'])

RECIFE = [-8.053849368460197, -34.87894208907804]
CARUARU = [-8.281975169821116, -35.96588785097934]
PETROLINA = [-9.387846231355782, -40.513466676896314]
JABOATAO = [-8.150522392722545, -34.93080508612456]
OLINDA = [-8.013680618252561, -34.84965808906329]

coord_cidades_mais_casos = np.array([RECIFE, CARUARU, PETROLINA, JABOATAO, OLINDA])

df_5_coord = pd.DataFrame(coord_cidades_mais_casos, columns=['latitude', 'longitude'])

df_5 = df_qt5_max.iloc[:5, :]
df_5.loc[:, 'lat'] = coord_cidades_mais_casos[:, 0]
df_5.loc[:, 'lon'] = coord_cidades_mais_casos[:, 1]

df_5 = df_5.reset_index(drop=True)

# Questao 6 #

df_ultima_semana_6 = df_covid[df_covid['semanaEpi'] == df_covid['semanaEpi'].max() - 1]

df_ultima_semana_6 = df_ultima_semana_6[df_ultima_semana_6['regiao'] != "Brasil"]
df_ultima_semana_6 = df_ultima_semana_6[df_ultima_semana_6['municipio'].isna() & df_ultima_semana_6['codmun'].isna()][['regiao', 'estado', 'semanaEpi', 'casosNovos', 'obitosNovos']]

df_agrupado_qt6 = df_ultima_semana_6.groupby(["estado", "semanaEpi"]).agg({
    'estado': 'first',
    'semanaEpi': 'first',
    'casosNovos': 'sum',
    'obitosNovos': 'sum'
    })

df_agrupado_qt6 = df_agrupado_qt6.reset_index(drop=True)


# Questão 7 #
regioes_qt7 = ['Norte', 'Nordeste', 'Sudeste']

df_covid_qt7 = df_covid[df_covid['regiao'].isin(regioes_qt7)]
df_covid_qt7 = df_covid_qt7[df_covid_qt7['municipio'].isna() & df_covid_qt7['codmun'].isna()][['regiao', 'estado', 'casosNovos', 'semanaEpi', 'data']]

#agregação por semana epidemiológica
#df_agrupado_qt7 = df_covid_qt7.groupby(["semanaEpi", "regiao"]).agg({
#    'semanaEpi': 'first',
#    'regiao': 'first',    
#    'casosNovos': 'sum'
#    })

df_agrupado_qt7 = df_covid_qt7.groupby(["data", "semanaEpi", "regiao"]).agg({
    'semanaEpi': 'first',
    'regiao': 'first',
    'data': 'first',    
    'casosNovos': 'sum'
    })

df_agrupado_qt7 = df_agrupado_qt7.reset_index(drop=True)

# Questão 8 #
# Regiao escolhida: Centro-oeste
df_covid_qt8 = df_covid[df_covid['regiao'] == 'Centro-Oeste']
df_covid_qt8 = df_covid_qt8[df_covid_qt8['municipio'].isna() & df_covid_qt8['codmun'].isna()][['regiao', 'estado', 'casosNovos', 'semanaEpi']]

#agregação por semana epidemiológica
df_agrupado_qt8 = df_covid_qt8.groupby(["semanaEpi", "regiao"]).agg({
    'semanaEpi': 'first',
    'regiao': 'first',
    'casosNovos': 'sum'
    })

df_agrupado_qt8 = df_agrupado_qt8.reset_index(drop=True)

# Questão 9 #
### Heat MAP ###
#casos novos, óbitos novos e leitos hospitalares ocupados (não disponível no dataset)

df_covid_qt9 = df_covid[df_covid['estado'] == 'PE']
df_covid_qt9 = df_covid_qt9[df_covid_qt9['municipio'].isna() & df_covid_qt9['codmun'].isna()][['estado', 'semanaEpi', 'casosNovos', 'obitosNovos']]

# Necessário agregar os casos novos por semana, pois a base de dados registra uma entrada por data
df_agrupado_qt9 = df_covid_qt9.groupby(["semanaEpi"]).agg({
    'estado': 'first',
    'casosNovos': 'sum',
    'obitosNovos': 'sum'
    })

df_agrupado_qt9['semanaEpi'] = df_agrupado_qt9.index
df_agrupado_qt9 = df_agrupado_qt9.reset_index(drop=True)

# Questao 10
# Gráfico de pizza plotly
# Distribuição dos casos acumulados de COVID 19 entre as cinco regiões do Brasil
df_ultima_semana_10 = df_covid[df_covid['semanaEpi'] == df_covid['semanaEpi'].max()]
df_ultima_semana_10 = df_ultima_semana_10[df_ultima_semana_10['regiao'] != "Brasil"]
df_ultima_semana_10 = df_ultima_semana_10[df_ultima_semana_10['municipio'].isna() & df_ultima_semana_10['codmun'].isna()][['regiao', 'semanaEpi', 'casosAcumulado']]

df_agrupado_qt10 = df_ultima_semana_10.groupby(['regiao']).agg({
    'semanaEpi': 'first',
    'casosAcumulado': 'sum',
    })

df_agrupado_qt10['regiao'] = df_agrupado_qt10.index
df_agrupado_qt10 = df_agrupado_qt10[['regiao', 'semanaEpi', 'casosAcumulado']].reset_index(drop=True)

# Questao 11
regioes_qt11 = ['Nordeste', 'Sul']

df_covid_qt11 = df_covid[df_covid['regiao'].isin(regioes_qt11)]
df_covid_qt11 = df_covid_qt11[df_covid_qt11['municipio'].isna() & df_covid_qt11['codmun'].isna()][['regiao', 'estado', 'semanaEpi', 'casosNovos', 'obitosNovos']]

#agregação por semana epidemiológica
df_agrupado_qt11 = df_covid_qt11.groupby(["semanaEpi", "regiao"]).agg({
    'semanaEpi': 'first',
    'regiao': 'first',
    'casosNovos': 'sum',
    'obitosNovos': 'sum'
    })

df_agrupado_qt11 = df_agrupado_qt11.reset_index(drop=True)

# Questao 12
# Aproveitar o dataframe processado para a questão 5, por ser iniviável a realização com todos os municípios de um Estado

#####################################################################################################################################

### Visualizações e respostas textuais ###
# Foram utilizados os arquivos referentes ao ano de 2025

st.title("TP 2 - Visualização de dados com Streamlit")

# Questão 1 #
# A visualização de dados em geral e, em especial, nas situações de crises graves de saúde, como foi o caso da pandemia de COVID-19, é de especial interesse, pois favorece uma compreensão mais rápida dos dados disponíveis, propiciando a tomada de atitudes de forma tempestiva. 
# Para as autoridades, visualizar os dados permite verificar com clareza as melhores formas de alocar recursos materiais e humanos, de acordo com as necessidades e lacunas observadas em cada área do espaço geográfico e, para o público em geral, favorece o ajuste do nível de precaução adequado à situação atual representada pelos dados.

# Questão 2 #
# Gráfico de barras - evolução dos casos - em um Estado
# Estado: AM, escolhido para verificar retorno à normalidade após as crises graves durante a época da pandemia

st.subheader("Questão 2")
st.bar_chart(df_agrupado_qt2, x='semanaEpi', y='casosNovos')

# Questão 3 #
# Gráfico de linha - óbitos acumulados - Brasil

# O gráfico mostra uma variação de aproximadamente 200 óbitos. A curva se mantém quase constante aos olhos porque a variação não se destaca ante o acumulado de mais de 700.000 óbitos

st.subheader("Questão 3")
st.line_chart(df_agrupado_qt3, x="semanaEpi", y="obitosAcumulado")

# Questão 4 #
# Casos acumulados, gráfico de área, 3 Estados
# Estados: AM, RS, SP

# Como já visto na questão 3, a variação no total de óbitos acumulados é pequena, portanto o gráfico tem a aparência de 3 retângulos sobrepostos. Vê-se apenas variações nas tonalidades de vermelho devido à sobreposição das cores correspondentes aos Estados. E possível verificar que os limites das cores correspondem às metricas: aprox. 7mi para SP, aprox. 3,1mi para o RS e aprox. 650mil para AM

st.subheader("Questão 4")

st.area_chart(
    df_agrupado_qt4,
    x="semanaEpi",
    y="casosAcumulado",
    color='estado'
)

# Questão 5 #

# O gráfico expõe a diferença na distribuição de casos acumulados entre os municípios apontados, de maneira que é possível rapidamente fazer uma comparação entre suas métricas a partir de uma observação geográfica.
st.subheader("Questão 5")
'Cinco cidades com maior incidência de casos de COVID-19 em PE: ', " ".join(cidades_mais_casos), '.'

casos_5 = np.array(df_5['casosAcumulado'] * 0.002)
casos_5 = [int(caso) for caso in casos_5]
df_5.loc[:, 'marcadores'] = casos_5

st.map(
    data=df_5,
    latitude='lat',
    longitude='lon',
    size='marcadores',
    color="#FF4B4B"
    )

# Questão 6 #

# Utilizei dados da penúltima semana, pois os dados de casos novos e óbitos novos referentes à ultima semana estavam zerados. Observa-se no gráfico (ano 2025, portanto pós-pandêmico) a prevalência da notificação de novos casos sobre os óbitos por COVID-19. Isso mostra o controle da doença alcançado após a pandemia. É possível observar topos discretos em laranja em cima das barras, corresnpondendo às novas mortes.

st.subheader("Questão 6")

estados = list(df_agrupado_qt6['estado'])
fig, ax = plt.subplots()

# Base
ax.bar(df_agrupado_qt6['estado'], df_agrupado_qt6['casosNovos'], label='Casos novos', color='#1f77b4')

# Segunda camada acima
ax.bar(df_agrupado_qt6['estado'], df_agrupado_qt6['obitosNovos'], bottom=df_agrupado_qt6['casosNovos'], label='Óbitos novos', color='#ff7f0e')

# Ajustes
ax.tick_params(axis='x', labelrotation=45)
ax.set_ylabel('Nº de casos')
ax.set_title('Casos Novos e Obitos Novos (Barras Empilhadas)')
ax.legend()

st.pyplot(fig)

# Questão 7 #
# Seaborn, novos casos por semana, comparação entre Norte, NE, SE
# A caixa do bloxplot não fica visível, pois na maior parte das semana há reporte de novos casos em apenas um dia (representado pelos círculos - outliers superiores). As observações dos dias sem novos casos ficam concentradas em y=0.

st.subheader("Questão 7")
st.dataframe(df_agrupado_qt7)

sns.set_theme(style="darkgrid")
fig_7, ax_7 = plt.subplots()
sns.boxplot(data=df_agrupado_qt7, x=df_agrupado_qt7['semanaEpi'], y=df_agrupado_qt7['casosNovos'], hue=df_agrupado_qt7['regiao'])

st.pyplot(fig_7) 

# Questão 8 #
# Gráfico de área Altair, casos novos por semana em uma região
# Região escolhida: Centro-Oeste, para ter mais familiaridade com os dados dessa região.
# O gráfico mostra um pico na semana 1, decaindo na semana 2 e subindo até um topo na semana 11 (aprox. 3000 novos casos). Na semana 10 há um reporte negativo, provavelmente devido a alguma retificação nos dados, o mesmo ocorre na semana 15, 30, 31 e ,32. A partir da semana 12, há 3 pequenos picos (na casa das milhares - semanas 13, 19 e 35); as demais semanas têm report abaixo de 1000 novos casos 

st.subheader("Questão 8")
chart_8 = alt.Chart(df_agrupado_qt8).mark_area().encode(
    x = 'semanaEpi',  
    y = 'casosNovos',
)

st.altair_chart(chart_8)

# Questão 9 #
# Heatmap com Altair
# Dados sobre leitos hospitalares ocupados não estão disponíveis
# Gráfico montado com obitos novos no eixo X e casos novos no eixo Y
# Colorido por óbitos novos

# Os retângulos formados não mostram exatamente correlações devido ao tipo dos dados. Graficos de calor que mostram correlação normalmente comparam muitos pares de atributos. No entanto, o gráfico mostra os dados relativos aos retângulos coloridos formados, ao se passar o mouse sobre eles, demonstrando a correspondência entre os valores presentes naquele local do gráfico (valores dos eixos x e y, bem como o registro da cor - referênte à semana epidemiológica)

st.subheader('Questão 9')

st.dataframe(df_agrupado_qt9)
#X, Y = np.meshgrid(x_axis, y_axis)

heatmap_9 = alt.Chart(df_agrupado_qt9).mark_rect().encode(
    y='casosNovos',
    x='obitosNovos',
    color='semanaEpi'
)

st.altair_chart(heatmap_9)

# Questão 10 #

# O percentual de casos acumulados é aproxmadamente proporcional às populações de cada região, apenas invertendo a ordem entre Nordeste e Sul, e entre o Centro-Oeste e o Norte; dentro de uma margem de aproximadamente 3%

st.subheader('Questão 10')
px_fig = px.pie(
    df_agrupado_qt10,
    names=df_agrupado_qt10['regiao'],
    values=df_agrupado_qt10['casosAcumulado']
    )
st.plotly_chart(px_fig)

# Questão 11 #
st.subheader('Questão 11')

# Gráficos revelam picos de notificação de novos casos nas primeiras semanas. Considerando a diferença populacional, a região Sul apresenta percentual de mortes por habitante muito maior que a região Nordeste, as duas regiões apresentam taxas de mortalidade da ordem de poucas dezenas, porém a população no Nordeste é muito maior que a população do Sul.

fig1 = px.bar(df_agrupado_qt11[df_agrupado_qt11['regiao'] == 'Nordeste'], x='semanaEpi', y='casosNovos')
fig2 = px.bar(df_agrupado_qt11[df_agrupado_qt11['regiao'] == 'Nordeste'], x='semanaEpi', y='obitosNovos')
fig3 = px.bar(df_agrupado_qt11[df_agrupado_qt11['regiao'] == 'Sul'], x='semanaEpi', y='casosNovos')
fig4 = px.bar(df_agrupado_qt11[df_agrupado_qt11['regiao'] == 'Sul'], x='semanaEpi', y='obitosNovos')

fig = make_subplots(
    rows=2, 
    cols=2,  
    subplot_titles=(
        "NE Casos novos",
        "NE Óbitos novos",
        "Sul Casos novos",
        "Sul Óbitos novos"
        )
    )

for trace in fig1.data:
    fig.add_trace(trace, row=1, col=1)

for trace in fig2.data:
    fig.add_trace(trace, row=1, col=2)

for trace in fig3.data:
    fig.add_trace(trace, row=2, col=1)

for trace in fig4.data:
    fig.add_trace(trace, row=2, col=2)


st.plotly_chart(fig)

# Questão 12 #

# Complemento processamento dos dados 
pop_cidades_mais_casos = []

for cidade in cidades_mais_casos:
    pop = df_covid[df_covid['municipio'] == cidade]['populacaoTCU2019'].unique()
    pop_cidades_mais_casos.append(int(pop))

df_5.loc[:,'pop'] = pop_cidades_mais_casos

area_recife = 218
area_caruaru = 920
area_petrolina = 4562
area_jaboatao = 258
area_olinda = 41

areas = np.array([area_recife, area_caruaru, area_petrolina, area_jaboatao, area_olinda])

df_5.loc[:, 'area_cidade'] = areas

den_pop_ajuste = np.array(df_5['pop'] / df_5['area_cidade'])
den_pop_ajuste = [int(pop * 0.1) for pop in den_pop_ajuste]

den_pop_ajuste

df_5.loc[:, 'den_pop_ajuste'] = den_pop_ajuste 

# Visualização

# A densidade populacional tende a aumentar a disseminação dos casos de COVID pela ocorrência de um número maior de pessoas no espaço. É possível observar que as duas cidades com maior incidência de casos são exatamente as duas cidades com as maiores populações.

# Comentários aos dados ; visualilzação:
# Os dados observados na capital (Recife) seguem essa tendência.
# Observam-se algumas discrepâncias quanto à relação entre densidade e quantidade de casos é observada, não acompanhando a regra 'maior densidade populacional: maio número de casos acumulados'.
# Olinda, especialmente, apresenta densidade populacional bastante alta, devido à sua área reduzida. 
# Jaboatão apresenta densidade populacional alta por se encontrar na região metropolitana do Recife e, portanto, ter uma quantidade de habitantes proporcionalmente maior que as cidades do interior (Caruaru e Petrolina). Entretanto a quantidade de casos acumulados é relatiivamente baixa, considerando a densidade populacional.
# Caruaru e Petrolina apresentam densidade populacional baixa por ocuparem áreas extensas. 
# Em linhas gerais, a quantidade de casos é proporcional às populações, mas não necessariamente à densidade populacional, nos dados observados.

st.subheader('Questão 12')

'''
**Mapa com PyDeck**
'''
'Regular zoom e arrastar o mapa para visualizar as cidades do interior'

coord_ini = [-8.096800506593977, -34.92077200112428]

# Densidade populacional (Scatterplot)
layer1 = pdk.Layer(
    "ScatterplotLayer",
    data=df_5,
    get_position=["lon", "lat"],
    get_radius="den_pop_ajuste",
    radius_scale=6,
    get_fill_color=[255, 0, 0, 160],
    pickable=True,
)

# Casos COVID (Barras)
layer2 = pdk.Layer(
    "ColumnLayer", 
    data=df_5, 
    get_position=["lon", "lat"],
    get_elevation='marcadores',
    radius=200, 
    opacity=0.5)

pe_initial_view = pdk.ViewState(latitude=coord_ini[0], longitude=coord_ini[1],
    zoom=11.5,
    pitch=85,
    bearing=0
)

deck = pdk.Deck(initial_view_state=pe_initial_view, map_style='road', layers=[layer1, layer2])

st.pydeck_chart(deck)

'''
**Dados da visualização**
'''

st.dataframe(df_5)