
# Lisa Troconis Reiners

## Descarga de Paquetes Relevantes
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import nltk
import numpy as np
from matplotlib import pyplot as plt
import re 
import string
import seaborn as sns

from nltk.corpus import stopwords # Elimina Palabras Vacias
from nltk.stem.lancaster import LancasterStemmer

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
#access drive
from google.colab import drive
drive.mount('/content/drive')

from textblob import TextBlob
import os
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
stop = stopwords.words('spanish')
from __future__ import print_function
from nltk.stem import *
from nltk.stem.porter import *
stemmer = PorterStemmer()

#descarga de librerias para los wordclouds

import wordcloud
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
import tkinter

#Importar la Base 
raw_acnur = pd.ExcelFile('DEEP_TESIS.xlsx') 
raw_acnur.sheet_names

#Seleccionar la Hoja Split Entries
df2 = raw_acnur.parse(0)
df2[50:150]
df2.head()

df2.shape

df2.dtypes

#Conteo de Vacios por Variable 
df2.isnull().sum()

# Seleccion de las Variables a estudiar 
df3 = df2[["Author", "Modified Excerpt" ,"AFFECTED GROUPS - Level 3"]]
#df3.iloc[:,3:4]
df3

# Modificacion del Nombre de las Variables 
df3 = df3.rename(columns = {"AFFECTED GROUPS - Level 3" : "Categoria", "Modified Excerpt" : "parrafos"})
df3.head()

#Suma el numero de Vacios
df3.isnull().sum()

#Forma del data frame
df3.shape

#Eliminar todos los Vacios de las categorias 
df3[df3.Categoria.isnull()]
df3 = df3.dropna(how = "any")
df3.shape

#Conteo de Vacios
df3.isnull().sum()

# drop rows which have same order_id
# and customer_id and keep latest entry
df3 = df3.drop_duplicates(
  subset = ['parrafos', 'Categoria'],
  keep = 'last').reset_index(drop = True)

df3.shape
df3

agrup = df3.groupby(["parrafos", "Categoria"])
agrup.first()

#agrup.get_group((" Salud: >5400 refugiados y migrantes recibieron consultas de atención primaria en salud y >800 recibieron información, educación y\ncomunicación en salud","Migrants"))

#Convertir en variables dummies/dicotomicas
dummies = pd.get_dummies(df3.Categoria)
df5 = pd.concat([df3,dummies],axis=1)
df5.head()

df5.info()
##There are not misssing Values

#Eliminar todos los textos que tienen https 
df5 = df5[~df5.parrafos.str.contains("https://")]
df5.shape

df5.Migrants.value_counts(normalize=True)
df5.Host.value_counts(normalize=True)
df5.IDP.value_counts(normalize=True)
df5.Returnees.value_counts(normalize=True)
df5.Refugees.value_counts(normalize=True)

# Crear una nueva base con el conteo 
df5_count = df5.iloc[:,4:].sum()
df5_count

#Tamano de el grafico
plt.figure(figsize = (10,6))

# Crear el grafico 
ax = sns.barplot(df5_count.index,df5_count.values, alpha = 0.5)
plt.title("Número de texto por categorías ")
plt.ylabel("Número de ocurrencias", fontsize = 12)
plt.xlabel("Categorías", fontsize = 12)

##Agregar los valores encima de las barras de cada categoria
rects = ax.patches
labels = df5_count.values
for rect, label in zip(rects, labels):
  height  = rect.get_height()
  ax.text(rect.get_x() + rect.get_width()/2, height + 5, label, ha = "center", va ="bottom")

# Tamano del dataframe
n_rows = len(df5)

#Tamano de el grafico
plt.figure(figsize = (10,6))

#Grafico de barras de porcentajes
shost = df5["Host"].sum()/n_rows * 100
sidp = df5["IDP"].sum()/n_rows * 100
smigrants = df5["Migrants"].sum()/n_rows * 100
snonhost = df5["Non Host"].sum()/n_rows * 100
srefugees = df5["Refugees"].sum()/n_rows * 100
sreturnees = df5["Returnees"].sum()/n_rows * 100

#Inicializar la variables ya que son 6 categorias
ind = np.arange(6)

ax = plt.barh(ind, [shost, sidp, smigrants,snonhost,srefugees,sreturnees])
plt.title("Porcentaje por categoría")
plt.xlabel("porcentaje (%)", fontsize = 12)
plt.yticks(ind, ("Host","IDP","Migrants","Non Host", "Refugees", "Returnees"))

#Poner el grafico de forma descendientes

plt.gca().invert_yaxis()
plt.show

df5[["parrafos"]]

import re
import string

def clean_text_round1(text):
    '''Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.'''
    text = text.lower()
    text = re.sub('\[.*?\r\r]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)
    text = re.sub(r" ", " ", text)
    return text

round1 = lambda x: clean_text_round1(x)
data_clean = pd.DataFrame(df5.parrafos.apply(round1))
data_clean

# Apply a second round of cleaning
def clean_text_round2(text):
    '''Get rid of some additional punctuation and non-sensical text that was missed the first time around.'''
    text = re.sub('[‘’“”""\\r\r•…]', '', text)
    text = re.sub('\n', '', text)
    return text

round2 = lambda x: clean_text_round2(x)
# Let's take a look at the updated text
data_clean = pd.DataFrame(data_clean.parrafos.apply(round2))
data_clean

data_clean = data_clean.rename(columns = {"parrafos" : "parrafo_limpio"})
data_clean

#concateno las 2 bases de datos la limpia y la df5 para seleccionar las variables 
new_dc = pd.concat([df5, data_clean], axis=1)
new_dc

# Seleccion de las Variables a estudiar 
data = new_dc[["Author", "parrafo_limpio", "Migrants", "Refugees", "Returnees",'Host']]
data

! pip install langdetect

from langdetect import detect
data['langue'] = data['parrafo_limpio'].apply(detect)

data["langue"].unique()

#Selecciono la base con el lenguaje con mayor cantidad de texto por filas (Espanol)
dl = data.langue.value_counts()
dl

#Tamano de el grafico
plt.figure(figsize = (10,6))

# Crear el grafico 
ax = sns.barplot(dl.index,dl.values, alpha = 0.5)
plt.title("Número de textos por Idioma ")
plt.ylabel("Número de ocurrencias", fontsize = 12)
plt.xlabel("Idioma", fontsize = 12)

##Agregar los valores encima de las barras de cada categoria
rects = ax.patches
labels = dl.values
for rect, label in zip(rects, labels):
  height  = rect.get_height()
  ax.text(rect.get_x() + rect.get_width()/2, height + 5, label, ha = "center", va ="bottom")

#Crear base solo en espanol 
data_ES = data.loc[(data.langue == "es")]
data_ES



data_ES['parrafo_limpio'] = data_ES['parrafo_limpio'].apply(lambda x: ' '.join([item for item in x.split() if item not in stop]))

data_ES['parrafo_limpio'] = data_ES.apply(lambda row: nltk.word_tokenize(row['parrafo_limpio']), axis=1)

data_ES['parrafo_limpio'] = data_ES['parrafo_limpio'].apply(lambda x: [stemmer.stem(y) for y in x]) # Stem every word.

def join_item(item):
    return ' '.join(item)

data_ES["parrafo_join"] = data_ES.parrafo_limpio.apply(join_item)

data_final = data_ES[["parrafo_join" ,"Migrants", "Refugees", "Returnees", "Host"]]
data_final.shape

data_final

#plot new
# Crear una nueva base con el conteo 
data_final_count = data_final.iloc[:,1:].sum()
data_final_count

#Tamano de el grafico
plt.figure(figsize = (10,6))

# Crear el grafico 
ax = sns.barplot(data_final_count.index,data_final_count.values, alpha = 0.5)
plt.title("Número de texto por categorías ")
plt.ylabel("Número de ocurrencias", fontsize = 12)
plt.xlabel("Categorías", fontsize = 12)

##Agregar los valores encima de las barras de cada categoria
rects = ax.patches
labels = data_final_count.values
for rect, label in zip(rects, labels):
  height  = rect.get_height()
  ax.text(rect.get_x() + rect.get_width()/2, height + 5, label, ha = "center", va ="bottom")

#Tamano de el grafico
plt.figure(figsize = (10,6))

#Grafico de barras de porcentajes
shost = data_final["Host"].sum()/n_rows * 100
smigrants = data_final["Migrants"].sum()/n_rows * 100
srefugees = data_final["Refugees"].sum()/n_rows * 100
sreturnees = data_final["Returnees"].sum()/n_rows * 100

#Inicializar la variables ya que son 6 categorias
ind = np.arange(4)

ax = plt.barh(ind, [shost, smigrants,srefugees,sreturnees])
plt.title("Porcentaje por categoría")
plt.xlabel("porcentaje (%)", fontsize = 12)
plt.yticks(ind, ("Host","Migrants","Refugees", "Returnees"))

#Poner el grafico de forma descendientes

plt.gca().invert_yaxis()
plt.show

# Display the generated image:

plt.figure(figsize = (10,10))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

data_migra = data_ES[["parrafo_join" ,"Migrants"]]
subset_migra = data_migra[data_migra["Migrants"] == 1]

def nonan(x):
    if type(x) == str:
        return x.replace("\n", "")
    else:
        return ""

text = ' '.join([nonan(abstract) for abstract in subset_migra["parrafo_join"]])
wordcloud = WordCloud(max_font_size=None, background_color='black', collocations=False,
                      width=1200, height=1000).generate(text)

# Display the generated image:

plt.figure(figsize = (10,10))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

data_Host = data_ES[["parrafo_join" ,"Host"]]
subset_host = data_Host[data_Host["Host"] == 1]
def nonan(x):
    if type(x) == str:
        return x.replace("\n", "")
    else:
        return ""

text = ' '.join([nonan(abstract) for abstract in subset_host["parrafo_join"]])
wordcloud = WordCloud(max_font_size=None, background_color='black', collocations=False,
                      width=1200, height=1000).generate(text)

# Display the generated image:

plt.figure(figsize = (10,10))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

data_Refugees = data_ES[["parrafo_join" ,"Refugees"]]
subset_Refugees = data_Refugees[data_Refugees["Refugees"] == 1]
def nonan(x):
    if type(x) == str:
        return x.replace("\n", "")
    else:
        return ""

text = ' '.join([nonan(abstract) for abstract in subset_Refugees["parrafo_join"]])
wordcloud = WordCloud(max_font_size=None, background_color='black', collocations=False,
                      width=1200, height=1000).generate(text)

# Display the generated image:

plt.figure(figsize = (10,10))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

data_Returnees = data_ES[["parrafo_join" ,"Returnees"]]
subset_Returnees = data_Refugees[data_Returnees["Returnees"] == 1]
def nonan(x):
    if type(x) == str:
        return x.replace("\n", "")
    else:
        return ""

text = ' '.join([nonan(abstract) for abstract in subset_Returnees["parrafo_join"]])
wordcloud = WordCloud(max_font_size=None, background_color='black', collocations=False,
                      width=1200, height=1000).generate(text)

# Display the generated image:

plt.figure(figsize = (10,10))
plt.imshow(wordcloud)
plt.axis("off")
plt.show()

################################ Analisis de sentimiento ##################################
! pip install sentiment-analysis-spanish
! pip install keras tensorflow

f = data_final.iloc[1:50]
f = f["parrafo_join"]

f = f.drop_duplicates()

f = f.reset_index()  # make sure indexes pair with number of rows
for index, row in f.iterrows():
    print(row['parrafo_join'])

from sentiment_analysis_spanish import sentiment_analysis
sentiment = sentiment_analysis.SentimentAnalysisSpanish()
#f = f.reset_index()  # make sure indexes pair with number of rows
a=[]
for index, row in f.iterrows():
  b = sentiment.sentiment(row['parrafo_join'])
  a.append(b)
f["sentimental analysis"] = a
f

f = f[["parrafo_join",	"sentimental analysis"]]
f

##################################################################

data_final = data_final.reset_index(drop=True)
data_final

###################### Modelos  ###################

# Regresion logistica
train_data = data_final.dropna()
X = train_data.iloc[:,0]
y = train_data[['Migrants', 'Host', 'Refugees', "Returnees"]]

# Importing required libraries
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np

X

y

######## Separar para validacion cruzada 60% de entrenamiento , 20% de validacion y 20% de test

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.4, random_state=123)

X_test, X_val, y_test, y_val = train_test_split(X_test, y_test, test_size=0.5, random_state=123)


y_train  = round(y_train)
y_test = round(y_test)
y_val = round(y_val)

# Conerting text to TFIDF
from sklearn.feature_extraction.text import TfidfVectorizer
vect = TfidfVectorizer(decode_error='ignore')
train_tfidf = vect.fit_transform(X_train.values.astype('U')) 
val_tfidf = vect.transform(X_val.values.astype('U')) 
test_tfidf = vect.transform(X_test.values.astype('U'))

# Crear columnas vacias para llenarlas con las predicciones
col = ['Migrants', 'Host', 'Refugees', "Returnees"]
pred_train = np.zeros((X_train.shape[0],len(col)))
pred_test = np.zeros((X_test.shape[0],len(col)))
pred_val = np.zeros((X_val.shape[0],len(col)))

# Load Logistic Regression model
from sklearn.linear_model import LogisticRegression
LogR = LogisticRegression()

# Predict on train, val 
# Assuming that Data is linearly seperable
import numpy as np

y_train=y_train.astype('int')

for i,x in enumerate(col):
    LogR.fit(train_tfidf, y_train[x])
    pred_train[:,i] = LogR.predict_proba(train_tfidf)[:,1]
    pred_val[:,i] = LogR.predict_proba(val_tfidf)[:,1]
    print(x,"predicted!")

from sklearn import metrics
y_val = y_val.astype('int')
for i,x in enumerate(col):
    print(x,"<Train> AUC:",metrics.roc_auc_score(y_train[x], pred_train[:,i]), "             ","<Val> AUC:",metrics.roc_auc_score(y_val[x], pred_val[:,i]))

c=[0.01,0.1,1,10,100]
resultDict ={}
resultValDict ={}
for i in c:
    LogR = LogisticRegression(C=i)
    temp=[]
    temp2=[]
    for j,x in enumerate(col):
        LogR.fit(train_tfidf, y_train[x])
        pred_train[:,j] = LogR.predict_proba(train_tfidf)[:,1]
        pred_val[:,j] = LogR.predict_proba(val_tfidf)[:,1]
        temp.append(metrics.roc_auc_score(y_train[x], pred_train[:,1]))
        temp2.append(metrics.roc_auc_score(y_val[x], pred_val[:,1]))
    resultDict[i]=temp
    resultValDict[i]=temp2

result = pd.DataFrame(resultDict)
valResult =pd.DataFrame(resultValDict)

result , valResult , result-valResult

################################ Matplot ##################################
! pip install matplotlib
import matplotlib
import matplotlib.pyplot as pyplot

pyplot.subplot()
for i in result.index:
    pyplot.plot(c,(result - valResult).loc[i])
    
pyplot.xscale("log")
pyplot.xlabel("Value of C")
pyplot.ylabel("AUC Cross validation difference")
pyplot.legend(col)
pyplot.show()

LogR = LogisticRegression(C=0.1)
y_test = y_test.astype('int')
for i,x in enumerate(col):
    LogR.fit(train_tfidf, y_train[x])
    pred_test[:,i] = LogR.predict_proba(test_tfidf)[:,1]


for i,x in enumerate(col):
    print(x,"<Test> AUC:",metrics.roc_auc_score(y_test[x], pred_test[:,i]))
