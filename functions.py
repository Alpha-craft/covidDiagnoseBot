import numpy
import pandas
import random
import math
import time
import datetime
import operator
import requests
import pytz

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import RandomizedSearchCV, train_test_split
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

provinsi_indonesia = (
    'Aceh', 'Bali', 'Banten', 'Bengkulu', 'DI Yogyakarta', 'DKI Jakarta', 'Gorontalo', 'Jambi', 'Jawa Barat', 'Jawa Tengah', 'Jawa Timur', 
    'Kalimantan Barat', 'Kalimantan Selatan', 'Kalimantan Tengah', 'Kalimantan Timur', 'Kalimantan Utara', 'Kep. Bangka Belitung', 
    'Kep. Riau', 'Lampung', 'Maluku', 'Maluku Utara', 'Nusa Tenggara Barat', 'Nusa Tenggara Timur', 'Papua', 'Papua Barat', 'Riau', 'Sulawesi Barat', 
    'Sulawesi Selatan', 'Sulawesi Tengah', 'Sulawesi Tenggara', 'Sulawesi Utara', 'Sumatera Barat', 'Sumatera Selatan', 'Sumatera Utara'
)  

sw_factory = StopWordRemoverFactory()
# stopwords = sw_factory.get_stop_words()
sw_remover = sw_factory.create_stop_word_remover()

stemmer = StemmerFactory().create_stemmer()
rsp_list = pandas.read_csv("response.csv")
snt_list = pandas.read_csv("sentence.csv")
syn_list = pandas.read_csv("sinonim.csv")



def empty(lists):
  if len(lists) == 0:
    return True

  return False


def add_respon(responses, key):
  # mencari intent yang isinya seperti key pada dataframe lalu jadikan record
  getResponse = rsp_list[rsp_list["Intent"] == key].to_records(index=False)
  # jika getResponse tidak kosong maka tambahkan satu respon
  if not empty(getResponse):
    responses += [ random.choice(getResponse)[1] ]

  return responses




def get_responses(words, intents, current_responses):
  for word in words:
      for sentence in snt_list.itertuples():                
          if stemmer.stem(sentence.Sentence) == stemmer.stem(word) and sentence.Intent not in intents:   
            current_responses = add_respon(current_responses, sentence.Intent)
            
            intents += [ sentence.Intent ]


def inside(haystack, needlestack):
  for item in needlestack:
    if item in haystack:
      return True

  return False


def get_similarity_index(lists):
  lens = len(lists)
  list_index = list(range(0, lens))

  for x in range(lens):
    for y in range(lens):
      if lists[list_index[x]] > lists[list_index][y]:
        swap = list_index[x]
        list_index[x] = list_index[y]
        list_index[y] = swap

  return list_index


def synonymize(words):
  sinonim_list = syn_list.to_records(index=False)
  result = words.lower()

  for sinonims in sinonim_list:
    for item in str(sinonims[1]).split(','):
      result = result.replace(item, f"{sinonims[0]} ", 1)    

  return result


def is_topcases_province(search):
  get_province = requests.get("https://apicovid19indonesia-v2.vercel.app/api/indonesia/provinsi")
  province = get_province.json()

  topprovince = [x['provinsi'].lower() for x in province][:3]

  if search.replace('Kep.', 'Kepulauan').lower() in topprovince:
    return 1
  else:
    return 0


def get_province_stats(search):
  get_province = requests.get(f"https://apicovid19indonesia-v2.vercel.app/api/indonesia/provinsi?name={search.replace('Kep.', 'Kepulauan')}")
  province = get_province.json()[0]

  total = province['dirawat'] + province['meninggal'] + province['sembuh']
  x = (province['dirawat'] / total) * 100
  y = (province['meninggal'] / total) * 100
  z = (province['sembuh'] / total) * 100

  url = f"https://image-charts.com/chart?chco=9fc5e8|ef0d0d|8ef836&chd=t:{ x },{ y },{ z }&chs=700x500&cht=p3&chdl=dirawat|meninggal|sembuh&chma=0,0,40,0&chtt=Statistik covid { province['provinsi'] }&chts=000000,30&chl={ province['dirawat'] } Jiwa|{ province['meninggal'] } Jiwa|{ province['sembuh'] } Jiwa"

  return {
    "img_url": url, 
    "kasus": province['kasus'], 
    "dirawat": province['dirawat'], 
    "meninggal": province['meninggal'], 
    "sembuh": province['sembuh']
  }


def get_covid_info(user_input):
  response = None
  article = open("article.txt", "r")

  if len(user_input.split()) < 3:
    min_similarity = 0.4
  else:
    min_similarity = 0.1

  paragraph = article.read().split("\n\n\n")
  tokens = [ stemmer.stem(sw_remover.remove(synonymize(token))) for token in paragraph ]

  tokens.append(user_input)
  vectorized = CountVectorizer().fit_transform(tokens)
  similarity = cosine_similarity(vectorized[-1], vectorized)
  similarity_list = similarity.flatten()
  index = get_similarity_index(similarity_list)
  index = index[1:]

  print(similarity_list)

  for x in range(len(index)):
    if similarity_list[index[x]] > min_similarity:
      response = f"{paragraph[index[x]]}\n\n"
      break

  tokens.remove(user_input)

  return [ response ]




def get_covid_stats():
  try:
      now = datetime.datetime.now(pytz.timezone('Asia/Jakarta'))

      head = []
      data = []
      start = ''
      for x in range(1, 8):
          timey = now - datetime.timedelta(days=x)
          d = timey.strftime('%d')
          m = timey.strftime('%B')
          y = timey.strftime('%Y')

          get_covid = requests.get(f"https://apicovid19indonesia-v2.vercel.app/api/indonesia/provinsi/harian?year={y}&date={d}&month={m}")
          covid_info = get_covid.json() 

          if x == 7:
            start = timey.strftime('%d-%b')

          head += [ timey.strftime('%d-%b') ]
          data += [ covid_info['data'][0]['cur_total'] ]

      confirmed = pandas.DataFrame([data], columns = head)
      dates = confirmed.keys()
      cases = []

      for i in dates:
          cases.append(confirmed[i].sum())

      days_since = numpy.array([i for i in range(len(dates))]).reshape(-1, 1)
      cases = numpy.array(cases).reshape(-1, 1)

      days_in_future = 3
      future_forcast = numpy.array([i for i in range(len(dates)+days_in_future)]).reshape(-1, 1)

      start_date = datetime.datetime.strptime(start, '%d-%b')
      future_forcast_dates = []
      cases_date = []
      for i in range(len(future_forcast)):
          future_forcast_dates.append((start_date + datetime.timedelta(days=i)).strftime('%d-%b'))

      X_train_confirmed, X_test_confirmed, y_train_confirmed, y_test_confirmed = train_test_split(days_since, cases, test_size=0.15, shuffle=False) 

      kernel = ['poly', 'sigmoid', 'rbf']
      c = [0.01, 0.1, 1, 10]
      gamma = [0.01, 0.1, 1]
      epsilon = [0.01, 0.1, 1]
      shrinking = [True, False]
      svm_grid = {'kernel': kernel, 'C': c, 'gamma' : gamma, 'epsilon': epsilon, 'shrinking' : shrinking}

      svm = SVR()
      svm_search = RandomizedSearchCV(svm, svm_grid, scoring='neg_mean_squared_error', cv=3, return_train_score=True, n_jobs=-1, n_iter=40, verbose=1)
      svm_search.fit(X_train_confirmed, y_train_confirmed.ravel())

      svm_search.best_params_

      svm_confirmed = svm_search.best_estimator_
      svm_pred = svm_confirmed.predict(future_forcast)

      x = ''
      y = ''
      for i in cases:
          x += f'{round(i[0])},'
      for i in svm_pred:
          y += f'{round(i)},'
      x = x.rstrip(',')
      y = y.rstrip(',')

      return f"https://image-charts.com/chart?cht=lc&chd=a:|{ x }|{ y }&chdl=Prediksi|Positif&chxl=0:|{ '|'.join(future_forcast_dates) }|1:||1000|2500|5000|&chs=900x500&chco=3072F3,ff0000&chdlp=t&chls=2,4,1&chm=s,000000,0,-1,5|s,000000,1,-1,5&chxt=x,y"
  except:
      return False