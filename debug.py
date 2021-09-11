import numpy
import pandas
import random
import functions as func

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory # https://github.com/har07/PySastrawi

factory = StemmerFactory()
stemmer = factory.create_stemmer()
rsp_list = pandas.read_csv("response.csv")
snt_list = pandas.read_csv("sentence.csv")






active = True

while active:
  bot_respon = []
  detected_intent = []
  inp = input(": ")

  # loop sentence list yang diconvert ke tuple
  for item in snt_list.itertuples():    

    # jika intent covid terdeteksi    

    # jika stem dari sentence (kata dasar) dan intent belum ada di detected_intent..
    if stemmer.stem(item.Sentence) in inp and item.Intent not in detected_intent:   
      # jalankan function add response dan tambahkan intent kedalam detected_intent
      bot_respon = func.add_respon(bot_respon, item.Intent)
      detected_intent += [ item.Intent ]  

  func.get_covid_info(inp)

  # hasil akhir
  for item in bot_respon:
    print(item)    

  # untuk debug melihat intent
  # print(detected_intent)