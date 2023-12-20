import threading
from rekrute.scraping import scrape_rekrute
from emploi_ma.scraping import scrape_emploi_ma
from khdma_ma.scraping import scrape_khdma_ma
from marocannonces.scraping import scrape_marocannonces
from bayt.scraping import scrape_bayt
from linkedin.scraping import scrape_linkedin

max_pages = 5

thread_rekrute = threading.Thread(target=scrape_rekrute, args=("./rekrute/rekrute.csv", max_pages))
thread_emploi_ma = threading.Thread(target=scrape_emploi_ma, args=("./emploi_ma/emploi.ma.csv", max_pages))
thread_khdma_ma = threading.Thread(target=scrape_khdma_ma, args=("./khdma_ma/khdma.ma.csv", max_pages))
thread_marocannonces = threading.Thread(target=scrape_marocannonces, args=("./marocannonces/marocannonces.csv", max_pages))
thread_bayt = threading.Thread(target=scrape_bayt, args=("./bayt/bayt.csv",))
thread_linkedin = threading.Thread(target=scrape_linkedin, args=("./linkedin/linkedin.csv",))

thread_rekrute.start()
thread_emploi_ma.start()
thread_khdma_ma.start()
thread_marocannonces.start()
thread_bayt.start()
thread_linkedin.start()