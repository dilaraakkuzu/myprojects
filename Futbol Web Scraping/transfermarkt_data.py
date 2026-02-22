from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import time
from selenium.common.exceptions import NoSuchElementException
import csv
import pandas as pd
import sys
from selenium.webdriver.common.keys import Keys


 # Chrome seçeneklerini ayarla
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("user-data-dir=C:\\SeleniumChromeProfile")  # Yeni profil dizini
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--timeout=300")  # 5 dakikaya kadar bekleyebilir


#chrome_options.add_argument("--incognito")  # Gizli mod ekleniyor
#chrome_options.add_argument("--headless")  # Tarayıcı penceresi olmadan çalıştır
chrome_options.add_argument("--disable-gpu")  # GPU kullanımını devre dışı bırak (bazı sistemlerde gerekli)
 # WebDriver'i başlat 
league="super-lig"
season="2024"
driver_path="C:/Users/Dilara/Documents/ChromeDriver/chromedriver-win64/chromedriver.exe"
start_week="1"
end_week="27"
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)

wait = WebDriverWait(driver, 10)  # 10 saniyelik genel bir bekleme süresi

def player():
    time.sleep(3)
    driver.execute_script("window.scrollBy(0, 300);")  # 100 piksel aşağı kaydırır
    # 10 saniye boyunca belirli bir elementin görünmesini bekle
    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'tm-tabs'))
        )
    atm_tab=driver.find_elements(By.CLASS_NAME, 'tm-tabs')[0]
    detayli=atm_tab.find_elements(By.CLASS_NAME, 'tm-tab')[1]
    detayli.click()
    driver.execute_script("window.scrollBy(0, 300);")  # 100 piksel aşağı kaydırır
    table=driver.find_elements(By.CLASS_NAME, 'items')[0]
    tablex=table.find_elements(By.TAG_NAME, "tr")[1]
    wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'zentriert'))
        )
    x=tablex.find_elements(By.TAG_NAME, "td")
    kadro=x[3].text
    mac_sayisi=x[4].text
    mac_basina_puan_ortalaması=x[5].text
    gol_toplam=x[6].text
    kendi_kalesine_gol_toplam=x[7].text
    oyuna_girdigi=x[8].text
    oyundan_cıktı=x[9].text
    sari_kart_toplam=x[10].text
    sari_kirmizi_kart_toplam=x[11].text
    kirmizi_kart_toplam=x[12].text
    yenilen_gol_toplam=x[13].text
    gol_yemedigi_mac_toplam=x[14].text
    sure_toplam=x[15].text
    
    playerr = [kadro,mac_sayisi,mac_basina_puan_ortalaması,gol_toplam,kendi_kalesine_gol_toplam,oyuna_girdigi,oyundan_cıktı,sari_kart_toplam
               ,sari_kirmizi_kart_toplam,kirmizi_kart_toplam,yenilen_gol_toplam,gol_yemedigi_mac_toplam,sure_toplam]
    return playerr
    
def kadrolar():
    # Ana sekmenin ID'sini kaydet
    ana_sekmeye_don = driver.current_window_handle  
    time.sleep(5)
    driver.execute_script("window.scrollBy(0, 300);")
    element = wait.until(
        EC.presence_of_element_located((By.CLASS_NAME, 'responsive-table'))
        )
    responsiveTable=driver.find_elements(By.CLASS_NAME, 'responsive-table')
    home_table=responsiveTable[0]
    away_table=responsiveTable[1]
    
    home_rows = home_table.find_elements(By.CLASS_NAME, 'inline-table')  # Tablo içindeki satırları al inline-table
    away_rows= away_table.find_elements(By.CLASS_NAME, 'inline-table')  # Tablo içindeki satırları al
    home_players = []
    away_players = []
    i=1
    for x in home_rows:
        driver.execute_script("window.scrollBy(0, 300);")
        money_ = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
        ) 
        money_=x.find_elements(By.TAG_NAME, "tr")[1].text
        # Düzenli ifade ile "1.40 mil. €" formatındaki para değerini çek
        match = re.search(r'(\d+\.\d+\s+mil\.\s*€)', money_)
        # Eğer eşleşme varsa, değeri al
        money = match.group(1) if match else "Bilinmiyor"
        element = x.find_element(By.CLASS_NAME, "wichtig")  # Elementi bul
        member_name=element.text
        
        href_player = element.get_attribute("href")  # Href değerini al
        
        # Yeni sekme aç ve href_kadrolar sayfasına git
        driver.execute_script("window.open(arguments[0]);", href_player)

       # Tüm sekmeleri liste olarak al
        window_handles = driver.window_handles

        # Yeni açılan sekmeye geç
        driver.switch_to.window(window_handles[-1])

        # Sayfanın yüklenmesini bekle
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'responsive-table'))
            )
        time.sleep(1)

   
        #print("Yeni sekmede işlemler yapılıyor...")
        playerrDetails_home=[]
        playerrDetails_home.extend(player())
        
        home_team_member={
            f"{i}.home_name":member_name,
            f"{i}.home_money":money,
            f"{i}.home_table":playerrDetails_home[0],
            f"{i}.home_kadro":playerrDetails_home[1],
            f"{i}.home_mac_sayisi":playerrDetails_home[2],
            f"{i}.home_mac_basina_puan_ortalaması":playerrDetails_home[3],
            f"{i}.home_gol_toplam":playerrDetails_home[4],
            f"{i}.home_oyuna_girdigi":playerrDetails_home[5],
            f"{i}.home_oyundan_cıktı":playerrDetails_home[6],
            f"{i}.home_sari_kart_toplam":playerrDetails_home[7],
            f"{i}.home_sari_kirmizi_kart_toplam":playerrDetails_home[8],
            f"{i}.home_kirmizi_kart_toplam":playerrDetails_home[9],
            f"{i}.home_yenilen_gol_toplam":playerrDetails_home[10],
            f"{i}.home_gol_yemedigi_mac_toplam":playerrDetails_home[11],
            f"{i}.home_sure_toplam":playerrDetails_home[12],
            }
        i=i+1
        home_players.append(home_team_member)
        # İşlemler tamamlandıktan sonra sekmeyi kapat
        driver.close()

        # Ana sekmeye geri dön
        driver.switch_to.window(ana_sekmeye_don)

        #print("Ana sekmeye geri dönüldü!")
        
    #####################################AWAYYYY
    k=1 
    for x in away_rows:
        driver.execute_script("window.scrollBy(0, 300);")
        money_ = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "tr"))
        ) 
        money_=x.find_elements(By.TAG_NAME, "tr")[1].text
        # Düzenli ifade ile "1.40 mil. €" formatındaki para değerini çek
        match = re.search(r'(\d+\.\d+\s+mil\.\s*€)', money_)
        # Eğer eşleşme varsa, değeri al
        money = match.group(1) if match else "Bilinmiyor"
        element = x.find_element(By.CLASS_NAME, "wichtig")  # Elementi bul
        member_name=element.text
        
        href_player = element.get_attribute("href")  # Href değerini al
        # Yeni sekme aç ve href_kadrolar sayfasına git
        driver.execute_script("window.open(arguments[0]);", href_player)

       # Tüm sekmeleri liste olarak al
        window_handles = driver.window_handles

        # Yeni açılan sekmeye geç
        driver.switch_to.window(window_handles[-1])

        # Sayfanın yüklenmesini bekle
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'responsive-table'))
            )
        time.sleep(1)

    
        #print("Yeni sekmede işlemler yapılıyor...")
        
        playerrDetails_away=[]
        playerrDetails_away.extend(player())
        
        away_team_member={
            f"{k}.away_name":member_name,
            f"{k}.away_money":money,
            f"{k}.away_table":playerrDetails_away[0],
            f"{k}.away_kadro":playerrDetails_away[1],
            f"{k}.away_mac_sayisi":playerrDetails_away[2],
            f"{k}.away_mac_basina_puan_ortalaması":playerrDetails_away[3],
            f"{k}.away_gol_toplam":playerrDetails_away[4],
            f"{k}.away_oyuna_girdigi":playerrDetails_away[5],
            f"{k}.away_oyundan_cıktı":playerrDetails_away[6],
            f"{k}.away_sari_kart_toplam":playerrDetails_away[7],
            f"{k}.away_sari_kirmizi_kart_toplam":playerrDetails_away[8],
            f"{k}.away_kirmizi_kart_toplam":playerrDetails_away[9],
            f"{k}.away_yenilen_gol_toplam":playerrDetails_away[10],
            f"{k}.away_gol_yemedigi_mac_toplam":playerrDetails_away[11],
            f"{k}.away_sure_toplam":playerrDetails_away[12],
            }
        k=k+1
        away_players.append(away_team_member)
        # 🔹 Ana sekmeye geri dön
        # İşlemler tamamlandıktan sonra sekmeyi kapat
        driver.close()

        # Ana sekmeye geri dön
        driver.switch_to.window(ana_sekmeye_don)

        #print("Ana sekmeye geri dönüldü!")

    return home_players,away_players

def istatistik():
    time.sleep(3)
    home_istatistik = []
    away_istatistik= []
    
    awx=driver.find_elements(By.CLASS_NAME,"sb-statistik-heim")
    bwx=driver.find_elements(By.CLASS_NAME,"sb-statistik-gast")
    
    home_toplam_sut_=awx[0]
    home_toplam_sut=home_toplam_sut_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    home_isabetsiz_sut_=awx[1]
    home_isabetsiz_sut=home_isabetsiz_sut_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    home_kurtarıs_=awx[2]
    home_kurtarıs=home_kurtarıs_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    home_korner_=awx[3]
    home_korner=home_korner_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    home_serbest_vurus_=awx[4]
    home_serbest_vurus=home_serbest_vurus_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    home_faul_=awx[5]
    home_faul=home_faul_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    home_ofsayt_=awx[6]
    home_ofsayt=home_ofsayt_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    ###away
    away_toplam_sut_=bwx[0]
    away_toplam_sut=away_toplam_sut_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    away_isabetsiz_sut_=bwx[1]
    away_isabetsiz_sut=away_isabetsiz_sut_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    away_kurtarıs_=bwx[2]
    away_kurtarıs=away_kurtarıs_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    away_korner_=bwx[3]
    away_korner=away_korner_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    away_serbest_vurus_=bwx[4]
    away_serbest_vurus=away_serbest_vurus_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    away_faul_=bwx[5]
    away_faul=away_faul_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    away_ofsayt_=bwx[6]
    away_ofsayt=away_ofsayt_.find_element(By.CLASS_NAME,"sb-statistik-zahl").text
    
    home_istatistik = [home_toplam_sut,home_isabetsiz_sut,home_kurtarıs,home_korner,home_serbest_vurus,home_faul
                       ,home_ofsayt]
    away_istatistik = [away_toplam_sut,away_isabetsiz_sut,away_kurtarıs,away_korner,away_serbest_vurus,away_faul
                       ,away_ofsayt]
    
    return home_istatistik,away_istatistik
    
    
def mac_raporu():
    time.sleep(3)
    League=driver.find_element(By.CLASS_NAME,"direct-headline__link").text
    u=driver.find_elements(By.CLASS_NAME,"sb-vereinslink")
    home_team=u[0].text
    away_team=u[1].text
    score=driver.find_elements(By.CLASS_NAME,"sb-endstand")[0].text
    # Skoru temizle
    score_lines = score.split("\n")  # Satırlara ayır
    main_score = score_lines[0].strip()  # İlk satırı al ve boşlukları temizle
    home_score, away_score = map(str.strip, main_score.split(":"))  # Skoru ayır
    mac_raporu=[home_team,away_team,home_score,away_score,League]
    return mac_raporu
    

def kulup_karsilastirmalari():
    time.sleep(3)
    kulup = []
    x=driver.find_elements(By.CLASS_NAME,"datenundfakten_bar")
    
    home_toplam_deger=x[0].text
    away_toplam_deger=x[1].text
    
    home_ø_Piyasa_degeri=x[2].text
    away_ø_Piyasa_degeri=x[3].text
    
    kulup=[home_toplam_deger,home_ø_Piyasa_degeri,away_toplam_deger,away_ø_Piyasa_degeri]
    return kulup
    
    
def extract_data(href_match):
    time.sleep(2)
    match_data = []
    # Düzenli ifade ile takım isimleri ve match_id'yi çekme
    match = re.search(r"transfermarkt\.com\.tr/([^/]+)/index/spielbericht/(\d+)", href_match)
    takım_isimleri = match.group(1)  # İlk grup: takım isimleri
    match_id = match.group(2)        # İkinci grup: maç kimliği (ID)
    href_kadrolar=f"https://www.transfermarkt.com.tr/{takım_isimleri}/aufstellung/spielbericht/{match_id}"
    href_istatistik=f"https://www.transfermarkt.com.tr/{takım_isimleri}/statistik/spielbericht/{match_id}"
    href_kulüp_karşılaştırması=f"https://www.transfermarkt.com.tr/{takım_isimleri}/vorbericht/spielbericht/{match_id}"
    
    #MAÇ RAPORU
    mac_raporlari = []
    # Ana sekmenin ID'sini kaydet
    ana_sekmeye_don = driver.current_window_handle 
    # Yeni sekme aç ve href_kadrolar sayfasına git
    driver.execute_script("window.open(arguments[0]);", href_match)
    # Tüm sekmeleri liste olarak al
    window_handles = driver.window_handles
    # Yeni açılan sekmeye geç
    driver.switch_to.window(window_handles[-1])
    # Sayfanın yüklenmesini bekle
    time.sleep(3)
    mac_raporlari.extend(mac_raporu())
    #mac_raporu=[home_team,away_team,home_score,away_score,League]
    
    ##KADROLAR
    driver.get(href_kadrolar)
    time.sleep(3)
    home_list = []
    away_list = []
    home_players, away_players = kadrolar()  # Fonksiyondan gelen iki listeyi ayrıştır
    home_list.extend(home_players)
    away_list.extend(away_players)
    #print(away_list)

    
    ##ISTATISTIK
    home_istatistik = []
    away_istatistik = []
    driver.get(href_istatistik)
    time.sleep(3)
    home_istatistikk_, away_istatistikk_ = istatistik()  # Fonksiyondan gelen iki listeyi ayrıştır
    home_istatistik.extend(home_istatistikk_)
    away_istatistik.extend(away_istatistikk_)

    
    ##KULÜP KARŞILAŞTIRMALARI
    kulup_karsilastirmasi = []
    driver.get(href_kulüp_karşılaştırması)
    kulup_karsilastirmasi.extend(kulup_karsilastirmalari())
    
    # Maç verilerini tabloya ekleme
    match_data = {
        "Season":"2024-2025",
        "League":mac_raporlari[4],
        "Home Team": mac_raporlari[0],
        "Away Team": mac_raporlari[1],
        "Home Score": mac_raporlari[2],
        "Away Score": mac_raporlari[3],
        "1.Home Team Member Name": home_list[0]['1.home_name'],
        "2.Home Team Member Name": home_list[1]['2.home_name'],
        "3.Home Team Member Name": home_list[2]['3.home_name'],
        "4.Home Team Member Name": home_list[3]['4.home_name'],
        "5.Home Team Member Name": home_list[4]['5.home_name'],
        "6.Home Team Member Name": home_list[5]['6.home_name'],
        "7.Home Team Member Name": home_list[6]['7.home_name'],
        "8.Home Team Member Name": home_list[7]['8.home_name'],
        "9.Home Team Member Name": home_list[8]['9.home_name'],
        "10.Home Team Member Name": home_list[9]['10.home_name'],
        "11.Home Team Member Name": home_list[10]['11.home_name'],
        ##
        "1.Home Team Member Money": home_list[0]['1.home_money'],
        "2.Home Team Member Money": home_list[1]['2.home_money'],
        "3.Home Team Member Money": home_list[2]['3.home_money'],
        "4.Home Team Member Money": home_list[3]['4.home_money'],
        "5.Home Team Member Money": home_list[4]['5.home_money'],
        "6.Home Team Member Money": home_list[5]['6.home_money'],
        "7.Home Team Member Money": home_list[6]['7.home_money'],
        "8.Home Team Member Money": home_list[7]['8.home_money'],
        "9.Home Team Member Money": home_list[8]['9.home_money'],
        "10.Home Team Member Money": home_list[9]['10.home_money'],
        "11.Home Team Member Money": home_list[10]['11.home_money'],
        ##
        "1.Home Team Member Table": home_list[0]['1.home_table'],
        "2.Home Team Member Table": home_list[1]['2.home_table'],
        "3.Home Team Member Table": home_list[2]['3.home_table'],
        "4.Home Team Member Table": home_list[3]['4.home_table'],
        "5.Home Team Member Table": home_list[4]['5.home_table'],
        "6.Home Team Member Table": home_list[5]['6.home_table'],
        "7.Home Team Member Table": home_list[6]['7.home_table'],
        "8.Home Team Member Table": home_list[7]['8.home_table'],
        "9.Home Team Member Table": home_list[8]['9.home_table'],
        "10.Home Team Member Table": home_list[9]['10.home_table'],
        "11.Home Team Member Table": home_list[10]['11.home_table'],
        ##
        "1.Home Team Member Kadro": home_list[0]['1.home_kadro'],
        "2.Home Team Member Kadro": home_list[1]['2.home_kadro'],
        "3.Home Team Member Kadro": home_list[2]['3.home_kadro'],
        "4.Home Team Member Kadro": home_list[3]['4.home_kadro'],
        "5.Home Team Member Kadro": home_list[4]['5.home_kadro'],
        "6.Home Team Member Kadro": home_list[5]['6.home_kadro'],
        "7.Home Team Member Kadro": home_list[6]['7.home_kadro'],
        "8.Home Team Member Kadro": home_list[7]['8.home_kadro'],
        "9.Home Team Member Kadro": home_list[8]['9.home_kadro'],
        "10.Home Team Member Kadro": home_list[9]['10.home_kadro'],
        "11.Home Team Member Kadro": home_list[10]['11.home_kadro'],
        ##
        "1.Home Team Member Maç Sayısı": home_list[0]['1.home_mac_sayisi'],
        "2.Home Team Member Maç Sayısı": home_list[1]['2.home_mac_sayisi'],
        "3.Home Team Member Maç Sayısı": home_list[2]['3.home_mac_sayisi'],
        "4.Home Team Member Maç Sayısı": home_list[3]['4.home_mac_sayisi'],
        "5.Home Team Member Maç Sayısı": home_list[4]['5.home_mac_sayisi'],
        "6.Home Team Member Maç Sayısı": home_list[5]['6.home_mac_sayisi'],
        "7.Home Team Member Maç Sayısı": home_list[6]['7.home_mac_sayisi'],
        "8.Home Team Member Maç Sayısı": home_list[7]['8.home_mac_sayisi'],
        "9.Home Team Member Maç Sayısı": home_list[8]['9.home_mac_sayisi'],
        "10.Home Team Member Maç Sayısı": home_list[9]['10.home_mac_sayisi'],
        "11.Home Team Member Maç Sayısı": home_list[10]['11.home_mac_sayisi'],
        ##,
        "1.Home Team Member Maç Başına Puan Ortalaması": home_list[0]['1.home_mac_basina_puan_ortalaması'],
        "2.Home Team Member Maç Başına Puan Ortalaması": home_list[1]['2.home_mac_basina_puan_ortalaması'],
        "3.Home Team Member Maç Başına Puan Ortalaması": home_list[2]['3.home_mac_basina_puan_ortalaması'],
        "4.Home Team Member Maç Başına Puan Ortalaması": home_list[3]['4.home_mac_basina_puan_ortalaması'],
        "5.Home Team Member Maç Başına Puan Ortalaması": home_list[4]['5.home_mac_basina_puan_ortalaması'],
        "6.Home Team Member Maç Başına Puan Ortalaması": home_list[5]['6.home_mac_basina_puan_ortalaması'],
        "7.Home Team Member Maç Başına Puan Ortalaması": home_list[6]['7.home_mac_basina_puan_ortalaması'],
        "8.Home Team Member Maç Başına Puan Ortalaması": home_list[7]['8.home_mac_basina_puan_ortalaması'],
        "9.Home Team Member Maç Başına Puan Ortalaması": home_list[8]['9.home_mac_basina_puan_ortalaması'],
        "10.Home Team Member Maç Başına Puan Ortalaması": home_list[9]['10.home_mac_basina_puan_ortalaması'],
        "11.Home Team Member Maç Başına Puan Ortalaması": home_list[10]['11.home_mac_basina_puan_ortalaması'],
        ##
        "1.Home Team Member Gol Toplam": home_list[0]['1.home_gol_toplam'],
        "2.Home Team Member Gol Toplam": home_list[1]['2.home_gol_toplam'],
        "3.Home Team Member Gol Toplam": home_list[2]['3.home_gol_toplam'],
        "4.Home Team Member Gol Toplam": home_list[3]['4.home_gol_toplam'],
        "5.Home Team Member Gol Toplam": home_list[4]['5.home_gol_toplam'],
        "6.Home Team Member Gol Toplam": home_list[5]['6.home_gol_toplam'],
        "7.Home Team Member Gol Toplam": home_list[6]['7.home_gol_toplam'],
        "8.Home Team Member Gol Toplam": home_list[7]['8.home_gol_toplam'],
        "9.Home Team Member Gol Toplam": home_list[8]['9.home_gol_toplam'],
        "10.Home Team Member Gol Toplam": home_list[9]['10.home_gol_toplam'],
        "11.Home Team Member Gol Toplam": home_list[10]['11.home_gol_toplam'],
        ##
        "1.Home Team Member Oyuna Girdiği": home_list[0]['1.home_oyuna_girdigi'],
        "2.Home Team Member Oyuna Girdiği": home_list[1]['2.home_oyuna_girdigi'],
        "3.Home Team Member Oyuna Girdiği": home_list[2]['3.home_oyuna_girdigi'],
        "4.Home Team Member Oyuna Girdiği": home_list[3]['4.home_oyuna_girdigi'],
        "5.Home Team Member Oyuna Girdiği": home_list[4]['5.home_oyuna_girdigi'],
        "6.Home Team Member Oyuna Girdiği": home_list[5]['6.home_oyuna_girdigi'],
        "7.Home Team Member Oyuna Girdiği": home_list[6]['7.home_oyuna_girdigi'],
        "8.Home Team Member Oyuna Girdiği": home_list[7]['8.home_oyuna_girdigi'],
        "9.Home Team Member Oyuna Girdiği": home_list[8]['9.home_oyuna_girdigi'],
        "10.Home Team Member Oyuna Girdiği": home_list[9]['10.home_oyuna_girdigi'],
        "11.Home Team Member Oyuna Girdiği": home_list[10]['11.home_oyuna_girdigi'],
        ##
        "1.Home Team Member Oyundan Çıktığı": home_list[0]['1.home_oyundan_cıktı'],
        "2.Home Team Member Oyundan Çıktığı": home_list[1]['2.home_oyundan_cıktı'],
        "3.Home Team Member Oyundan Çıktığı": home_list[2]['3.home_oyundan_cıktı'],
        "4.Home Team Member Oyundan Çıktığı": home_list[3]['4.home_oyundan_cıktı'],
        "5.Home Team Member Oyundan Çıktığı": home_list[4]['5.home_oyundan_cıktı'],
        "6.Home Team Member Oyundan Çıktığı": home_list[5]['6.home_oyundan_cıktı'],
        "7.Home Team Member Oyundan Çıktığı": home_list[6]['7.home_oyundan_cıktı'],
        "8.Home Team Member Oyundan Çıktığı": home_list[7]['8.home_oyundan_cıktı'],
        "9.Home Team Member Oyundan Çıktığı": home_list[8]['9.home_oyundan_cıktı'],
        "10.Home Team Member Oyundan Çıktığı": home_list[9]['10.home_oyundan_cıktı'],
        "11.Home Team Member Oyundan Çıktığı": home_list[10]['11.home_oyundan_cıktı'],
        ##
        "1.Home Team Member Sarı Kart Toplam": home_list[0]['1.home_sari_kart_toplam'],
        "2.Home Team Member Sarı Kart Toplam": home_list[1]['2.home_sari_kart_toplam'],
        "3.Home Team Member Sarı Kart Toplam": home_list[2]['3.home_sari_kart_toplam'],
        "4.Home Team Member Sarı Kart Toplam": home_list[3]['4.home_sari_kart_toplam'],
        "5.Home Team Member Sarı Kart Toplam": home_list[4]['5.home_sari_kart_toplam'],
        "6.Home Team Member Sarı Kart Toplam": home_list[5]['6.home_sari_kart_toplam'],
        "7.Home Team Member Sarı Kart Toplam": home_list[6]['7.home_sari_kart_toplam'],
        "8.Home Team Member Sarı Kart Toplam": home_list[7]['8.home_sari_kart_toplam'],
        "9.Home Team Member Sarı Kart Toplam": home_list[8]['9.home_sari_kart_toplam'],
        "10.Home Team Member Sarı Kart Toplam": home_list[9]['10.home_sari_kart_toplam'],
        "11.Home Team Member Sarı Kart Toplam": home_list[10]['11.home_sari_kart_toplam'],
        ##
        "1.Home Team Member Sarı Kırmızı Toplam": home_list[0]['1.home_sari_kirmizi_kart_toplam'],
        "2.Home Team Member Sarı Kırmızı Toplam": home_list[1]['2.home_sari_kirmizi_kart_toplam'],
        "3.Home Team Member Sarı Kırmızı Toplam": home_list[2]['3.home_sari_kirmizi_kart_toplam'],
        "4.Home Team Member Sarı Kırmızı Toplam": home_list[3]['4.home_sari_kirmizi_kart_toplam'],
        "5.Home Team Member Sarı Kırmızı Toplam": home_list[4]['5.home_sari_kirmizi_kart_toplam'],
        "6.Home Team Member Sarı Kırmızı Toplam": home_list[5]['6.home_sari_kirmizi_kart_toplam'],
        "7.Home Team Member Sarı Kırmızı Toplam": home_list[6]['7.home_sari_kirmizi_kart_toplam'],
        "8.Home Team Member Sarı Kırmızı Toplam": home_list[7]['8.home_sari_kirmizi_kart_toplam'],
        "9.Home Team Member Sarı Kırmızı Toplam": home_list[8]['9.home_sari_kirmizi_kart_toplam'],
        "10.Home Team Member Sarı Kırmızı Toplam": home_list[9]['10.home_sari_kirmizi_kart_toplam'],
        "11.Home Team Member Sarı Kırmızı Toplam": home_list[10]['11.home_sari_kirmizi_kart_toplam'],
        ##
        "1.Home Team Member Kırmızı Toplam": home_list[0]['1.home_kirmizi_kart_toplam'],
        "2.Home Team Member Kırmızı Toplam": home_list[1]['2.home_kirmizi_kart_toplam'],
        "3.Home Team Member Kırmızı Toplam": home_list[2]['3.home_kirmizi_kart_toplam'],
        "4.Home Team Member Kırmızı Toplam": home_list[3]['4.home_kirmizi_kart_toplam'],
        "5.Home Team Member Kırmızı Toplam": home_list[4]['5.home_kirmizi_kart_toplam'],
        "6.Home Team Member Kırmızı Toplam": home_list[5]['6.home_kirmizi_kart_toplam'],
        "7.Home Team Member Kırmızı Toplam": home_list[6]['7.home_kirmizi_kart_toplam'],
        "8.Home Team Member Kırmızı Toplam": home_list[7]['8.home_kirmizi_kart_toplam'],
        "9.Home Team Member Kırmızı Toplam": home_list[8]['9.home_kirmizi_kart_toplam'],
        "10.Home Team Member Kırmızı Toplam": home_list[9]['10.home_kirmizi_kart_toplam'],
        "11.Home Team Member Kırmızı Toplam": home_list[10]['11.home_kirmizi_kart_toplam'],
        ##
        "1.Home Team Member Yenilen Gol Toplam": home_list[0]['1.home_yenilen_gol_toplam'],
        "2.Home Team Member Yenilen Gol Toplam": home_list[1]['2.home_yenilen_gol_toplam'],
        "3.Home Team Member Yenilen Gol Toplam": home_list[2]['3.home_yenilen_gol_toplam'],
        "4.Home Team Member Yenilen Gol Toplam": home_list[3]['4.home_yenilen_gol_toplam'],
        "5.Home Team Member Yenilen Gol Toplam": home_list[4]['5.home_yenilen_gol_toplam'],
        "6.Home Team Member Yenilen Gol Toplam": home_list[5]['6.home_yenilen_gol_toplam'],
        "7.Home Team Member Yenilen Gol Toplam": home_list[6]['7.home_yenilen_gol_toplam'],
        "8.Home Team Member Yenilen Gol Toplam": home_list[7]['8.home_yenilen_gol_toplam'],
        "9.Home Team Member Yenilen Gol Toplam": home_list[8]['9.home_yenilen_gol_toplam'],
        "10.Home Team Member Yenilen Gol Toplam": home_list[9]['10.home_yenilen_gol_toplam'],
        "11.Home Team Member Yenilen Gol Toplam": home_list[10]['11.home_yenilen_gol_toplam'],
        ##
        "1.Home Team Member Gol Yemediği Maç Toplam": home_list[0]['1.home_gol_yemedigi_mac_toplam'],
        "2.Home Team Member Gol Yemediği Maç Toplam": home_list[1]['2.home_gol_yemedigi_mac_toplam'],
        "3.Home Team Member Gol Yemediği Maç Toplam": home_list[2]['3.home_gol_yemedigi_mac_toplam'],
        "4.Home Team Member Gol Yemediği Maç Toplam": home_list[3]['4.home_gol_yemedigi_mac_toplam'],
        "5.Home Team Member Gol Yemediği Maç Toplam": home_list[4]['5.home_gol_yemedigi_mac_toplam'],
        "6.Home Team Member Gol Yemediği Maç Toplam": home_list[5]['6.home_gol_yemedigi_mac_toplam'],
        "7.Home Team Member Gol Yemediği Maç Toplam": home_list[6]['7.home_gol_yemedigi_mac_toplam'],
        "8.Home Team Member Gol Yemediği Maç Toplam": home_list[7]['8.home_gol_yemedigi_mac_toplam'],
        "9.Home Team Member Gol Yemediği Maç Toplam": home_list[8]['9.home_gol_yemedigi_mac_toplam'],
        "10.Home Team Member Gol Yemediği Maç Toplam": home_list[9]['10.home_gol_yemedigi_mac_toplam'],
        "11.Home Team Member Gol Yemediği Maç Toplam": home_list[10]['11.home_gol_yemedigi_mac_toplam'],
        ##
        "1.Home Team Member Süre Toplam": home_list[0]['1.home_sure_toplam'],
        "2.Home Team Member Süre Toplam": home_list[1]['2.home_sure_toplam'],
        "3.Home Team Member Süre Toplam": home_list[2]['3.home_sure_toplam'],
        "4.Home Team Member Süre Toplam": home_list[3]['4.home_sure_toplam'],
        "5.Home Team Member Süre Toplam": home_list[4]['5.home_sure_toplam'],
        "6.Home Team Member Süre Toplam": home_list[5]['6.home_sure_toplam'],
        "7.Home Team Member Süre Toplam": home_list[6]['7.home_sure_toplam'],
        "8.Home Team Member Süre Toplam": home_list[7]['8.home_sure_toplam'],
        "9.Home Team Member Süre Toplam": home_list[8]['9.home_sure_toplam'],
        "10.Home Team Member Süre Toplam": home_list[9]['10.home_sure_toplam'],
        "11.Home Team Member Süre Toplam": home_list[10]['11.home_sure_toplam'],
        #######################away
        "1.Away Team Member Name": away_list[0]['1.away_name'],
        "2.Away Team Member Name": away_list[1]['2.away_name'],
        "3.Away Team Member Name": away_list[2]['3.away_name'],
        "4.Away Team Member Name": away_list[3]['4.away_name'],
        "5.Away Team Member Name": away_list[4]['5.away_name'],
        "6.Away Team Member Name": away_list[5]['6.away_name'],
        "7.Away Team Member Name": away_list[6]['7.away_name'],
        "8.Away Team Member Name": away_list[7]['8.away_name'],
        "9.Away Team Member Name": away_list[8]['9.away_name'],
        "10.Away Team Member Name": away_list[9]['10.away_name'],
        "11.Away Team Member Name": away_list[10]['11.away_name'],
        ##
        "1.Away Team Member Money": away_list[0]['1.away_money'],
        "2.Away Team Member Money": away_list[1]['2.away_money'],
        "3.Away Team Member Money": away_list[2]['3.away_money'],
        "4.Away Team Member Money": away_list[3]['4.away_money'],
        "5.Away Team Member Money": away_list[4]['5.away_money'],
        "6.Away Team Member Money": away_list[5]['6.away_money'],
        "7.Away Team Member Money": away_list[6]['7.away_money'],
        "8.Away Team Member Money": away_list[7]['8.away_money'],
        "9.Away Team Member Money": away_list[8]['9.away_money'],
        "10.Away Team Member Money": away_list[9]['10.away_money'],
        "11.Away Team Member Money": away_list[10]['11.away_money'],
        ##
        "1.Away Team Member Table": away_list[0]['1.away_table'],
        "2.Away Team Member Table": away_list[1]['2.away_table'],
        "3.Away Team Member Table": away_list[2]['3.away_table'],
        "4.Away Team Member Table": away_list[3]['4.away_table'],
        "5.Away Team Member Table": away_list[4]['5.away_table'],
        "6.Away Team Member Table": away_list[5]['6.away_table'],
        "7.Away Team Member Table": away_list[6]['7.away_table'],
        "8.Away Team Member Table": away_list[7]['8.away_table'],
        "9.Away Team Member Table": away_list[8]['9.away_table'],
        "10.Away Team Member Table": away_list[9]['10.away_table'],
        "11.Away Team Member Table": away_list[10]['11.away_table'],
        ##
        "1.Away Team Member Kadro": away_list[0]['1.away_kadro'],
        "2.Away Team Member Kadro": away_list[1]['2.away_kadro'],
        "3.Away Team Member Kadro": away_list[2]['3.away_kadro'],
        "4.Away Team Member Kadro": away_list[3]['4.away_kadro'],
        "5.Away Team Member Kadro": away_list[4]['5.away_kadro'],
        "6.Away Team Member Kadro": away_list[5]['6.away_kadro'],
        "7.Away Team Member Kadro": away_list[6]['7.away_kadro'],
        "8.Away Team Member Kadro": away_list[7]['8.away_kadro'],
        "9.Away Team Member Kadro": away_list[8]['9.away_kadro'],
        "10.Away Team Member Kadro": away_list[9]['10.away_kadro'],
        "11.Away Team Member Kadro": away_list[10]['11.away_kadro'],
        ##
        "1.Away Team Member Maç Sayısı": away_list[0]['1.away_mac_sayisi'],
        "2.Away Team Member Maç Sayısı": away_list[1]['2.away_mac_sayisi'],
        "3.Away Team Member Maç Sayısı": away_list[2]['3.away_mac_sayisi'],
        "4.Away Team Member Maç Sayısı": away_list[3]['4.away_mac_sayisi'],
        "5.Away Team Member Maç Sayısı": away_list[4]['5.away_mac_sayisi'],
        "6.Away Team Member Maç Sayısı": away_list[5]['6.away_mac_sayisi'],
        "7.Away Team Member Maç Sayısı": away_list[6]['7.away_mac_sayisi'],
        "8.Away Team Member Maç Sayısı": away_list[7]['8.away_mac_sayisi'],
        "9.Away Team Member Maç Sayısı": away_list[8]['9.away_mac_sayisi'],
        "10.Away Team Member Maç Sayısı": away_list[9]['10.away_mac_sayisi'],
        "11.Away Team Member Maç Sayısı": away_list[10]['11.away_mac_sayisi'],
        ##,
        "1.Away Team Member Maç Başına Puan Ortalaması": away_list[0]['1.away_mac_basina_puan_ortalaması'],
        "2.Away Team Member Maç Başına Puan Ortalaması": away_list[1]['2.away_mac_basina_puan_ortalaması'],
        "3.Away Team Member Maç Başına Puan Ortalaması": away_list[2]['3.away_mac_basina_puan_ortalaması'],
        "4.Away Team Member Maç Başına Puan Ortalaması": away_list[3]['4.away_mac_basina_puan_ortalaması'],
        "5.Away Team Member Maç Başına Puan Ortalaması": away_list[4]['5.away_mac_basina_puan_ortalaması'],
        "6.Away Team Member Maç Başına Puan Ortalaması": away_list[5]['6.away_mac_basina_puan_ortalaması'],
        "7.Away Team Member Maç Başına Puan Ortalaması": away_list[6]['7.away_mac_basina_puan_ortalaması'],
        "8.Away Team Member Maç Başına Puan Ortalaması": away_list[7]['8.away_mac_basina_puan_ortalaması'],
        "9.Away Team Member Maç Başına Puan Ortalaması": away_list[8]['9.away_mac_basina_puan_ortalaması'],
        "10.Away Team Member Maç Başına Puan Ortalaması": away_list[9]['10.away_mac_basina_puan_ortalaması'],
        "11.Away Team Member Maç Başına Puan Ortalaması": away_list[10]['11.away_mac_basina_puan_ortalaması'],
        ##
        "1.Away Team Member Gol Toplam": away_list[0]['1.away_gol_toplam'],
        "2.Away Team Member Gol Toplam": away_list[1]['2.away_gol_toplam'],
        "3.Away Team Member Gol Toplam": away_list[2]['3.away_gol_toplam'],
        "4.Away Team Member Gol Toplam": away_list[3]['4.away_gol_toplam'],
        "5.Away Team Member Gol Toplam": away_list[4]['5.away_gol_toplam'],
        "6.Away Team Member Gol Toplam": away_list[5]['6.away_gol_toplam'],
        "7.Away Team Member Gol Toplam": away_list[6]['7.away_gol_toplam'],
        "8.Away Team Member Gol Toplam": away_list[7]['8.away_gol_toplam'],
        "9.Away Team Member Gol Toplam": away_list[8]['9.away_gol_toplam'],
        "10.Away Team Member Gol Toplam": away_list[9]['10.away_gol_toplam'],
        "11.Away Team Member Gol Toplam": away_list[10]['11.away_gol_toplam'],
        ##
        "1.Away Team Member Oyuna Girdiği": away_list[0]['1.away_oyuna_girdigi'],
        "2.Away Team Member Oyuna Girdiği": away_list[1]['2.away_oyuna_girdigi'],
        "3.Away Team Member Oyuna Girdiği": away_list[2]['3.away_oyuna_girdigi'],
        "4.Away Team Member Oyuna Girdiği": away_list[3]['4.away_oyuna_girdigi'],
        "5.Away Team Member Oyuna Girdiği": away_list[4]['5.away_oyuna_girdigi'],
        "6.Away Team Member Oyuna Girdiği": away_list[5]['6.away_oyuna_girdigi'],
        "7.Away Team Member Oyuna Girdiği": away_list[6]['7.away_oyuna_girdigi'],
        "8.Away Team Member Oyuna Girdiği": away_list[7]['8.away_oyuna_girdigi'],
        "9.Away Team Member Oyuna Girdiği": away_list[8]['9.away_oyuna_girdigi'],
        "10.Away Team Member Oyuna Girdiği": away_list[9]['10.away_oyuna_girdigi'],
        "11.Away Team Member Oyuna Girdiği": away_list[10]['11.away_oyuna_girdigi'],
        ##
        "1.Away Team Member Oyundan Çıktığı": away_list[0]['1.away_oyundan_cıktı'],
        "2.Away Team Member Oyundan Çıktığı": away_list[1]['2.away_oyundan_cıktı'],
        "3.Away Team Member Oyundan Çıktığı": away_list[2]['3.away_oyundan_cıktı'],
        "4.Away Team Member Oyundan Çıktığı": away_list[3]['4.away_oyundan_cıktı'],
        "5.Away Team Member Oyundan Çıktığı": away_list[4]['5.away_oyundan_cıktı'],
        "6.Away Team Member Oyundan Çıktığı": away_list[5]['6.away_oyundan_cıktı'],
        "7.Away Team Member Oyundan Çıktığı": away_list[6]['7.away_oyundan_cıktı'],
        "8.Away Team Member Oyundan Çıktığı": away_list[7]['8.away_oyundan_cıktı'],
        "9.Away Team Member Oyundan Çıktığı": away_list[8]['9.away_oyundan_cıktı'],
        "10.Away Team Member Oyundan Çıktığı": away_list[9]['10.away_oyundan_cıktı'],
        "11.Away Team Member Oyundan Çıktığı": away_list[10]['11.away_oyundan_cıktı'],
        ##
        "1.Away Team Member Sarı Kart Toplam": away_list[0]['1.away_sari_kart_toplam'],
        "2.Away Team Member Sarı Kart Toplam": away_list[1]['2.away_sari_kart_toplam'],
        "3.Away Team Member Sarı Kart Toplam": away_list[2]['3.away_sari_kart_toplam'],
        "4.Away Team Member Sarı Kart Toplam": away_list[3]['4.away_sari_kart_toplam'],
        "5.Away Team Member Sarı Kart Toplam": away_list[4]['5.away_sari_kart_toplam'],
        "6.Away Team Member Sarı Kart Toplam": away_list[5]['6.away_sari_kart_toplam'],
        "7.Away Team Member Sarı Kart Toplam": away_list[6]['7.away_sari_kart_toplam'],
        "8.Away Team Member Sarı Kart Toplam": away_list[7]['8.away_sari_kart_toplam'],
        "9.Away Team Member Sarı Kart Toplam": away_list[8]['9.away_sari_kart_toplam'],
        "10.Away Team Member Sarı Kart Toplam": away_list[9]['10.away_sari_kart_toplam'],
        "11.Away Team Member Sarı Kart Toplam": away_list[10]['11.away_sari_kart_toplam'],
        ##
        "1.Away Team Member Sarı Kırmızı Toplam": away_list[0]['1.away_sari_kirmizi_kart_toplam'],
        "2.Away Team Member Sarı Kırmızı Toplam": away_list[1]['2.away_sari_kirmizi_kart_toplam'],
        "3.Away Team Member Sarı Kırmızı Toplam": away_list[2]['3.away_sari_kirmizi_kart_toplam'],
        "4.Away Team Member Sarı Kırmızı Toplam": away_list[3]['4.away_sari_kirmizi_kart_toplam'],
        "5.Away Team Member Sarı Kırmızı Toplam": away_list[4]['5.away_sari_kirmizi_kart_toplam'],
        "6.Away Team Member Sarı Kırmızı Toplam": away_list[5]['6.away_sari_kirmizi_kart_toplam'],
        "7.Away Team Member Sarı Kırmızı Toplam": away_list[6]['7.away_sari_kirmizi_kart_toplam'],
        "8.Away Team Member Sarı Kırmızı Toplam": away_list[7]['8.away_sari_kirmizi_kart_toplam'],
        "9.Away Team Member Sarı Kırmızı Toplam": away_list[8]['9.away_sari_kirmizi_kart_toplam'],
        "10.Away Team Member Sarı Kırmızı Toplam": away_list[9]['10.away_sari_kirmizi_kart_toplam'],
        "11.Away Team Member Sarı Kırmızı Toplam": away_list[10]['11.away_sari_kirmizi_kart_toplam'],
        ##
        "1.Away Team Member Kırmızı Toplam": away_list[0]['1.away_kirmizi_kart_toplam'],
        "2.Away Team Member Kırmızı Toplam": away_list[1]['2.away_kirmizi_kart_toplam'],
        "3.Away Team Member Kırmızı Toplam": away_list[2]['3.away_kirmizi_kart_toplam'],
        "4.Away Team Member Kırmızı Toplam": away_list[3]['4.away_kirmizi_kart_toplam'],
        "5.Away Team Member Kırmızı Toplam": away_list[4]['5.away_kirmizi_kart_toplam'],
        "6.Away Team Member Kırmızı Toplam": away_list[5]['6.away_kirmizi_kart_toplam'],
        "7.Away Team Member Kırmızı Toplam": away_list[6]['7.away_kirmizi_kart_toplam'],
        "8.Away Team Member Kırmızı Toplam": away_list[7]['8.away_kirmizi_kart_toplam'],
        "9.Away Team Member Kırmızı Toplam": away_list[8]['9.away_kirmizi_kart_toplam'],
        "10.Away Team Member Kırmızı Toplam": away_list[9]['10.away_kirmizi_kart_toplam'],
        "11.Away Team Member Kırmızı Toplam": away_list[10]['11.away_kirmizi_kart_toplam'],
        ##
        "1.Away Team Member Yenilen Gol Toplam": away_list[0]['1.away_yenilen_gol_toplam'],
        "2.Away Team Member Yenilen Gol Toplam": away_list[1]['2.away_yenilen_gol_toplam'],
        "3.Away Team Member Yenilen Gol Toplam": away_list[2]['3.away_yenilen_gol_toplam'],
        "4.Away Team Member Yenilen Gol Toplam": away_list[3]['4.away_yenilen_gol_toplam'],
        "5.Away Team Member Yenilen Gol Toplam": away_list[4]['5.away_yenilen_gol_toplam'],
        "6.Away Team Member Yenilen Gol Toplam": away_list[5]['6.away_yenilen_gol_toplam'],
        "7.Away Team Member Yenilen Gol Toplam": away_list[6]['7.away_yenilen_gol_toplam'],
        "8.Away Team Member Yenilen Gol Toplam": away_list[7]['8.away_yenilen_gol_toplam'],
        "9.Away Team Member Yenilen Gol Toplam": away_list[8]['9.away_yenilen_gol_toplam'],
        "10.Away Team Member Yenilen Gol Toplam": away_list[9]['10.away_yenilen_gol_toplam'],
        "11.Away Team Member Yenilen Gol Toplam": away_list[10]['11.away_yenilen_gol_toplam'],
        ##
        "1.Away Team Member Gol Yemediği Maç Toplam": away_list[0]['1.away_gol_yemedigi_mac_toplam'],
        "2.Away Team Member Gol Yemediği Maç Toplam": away_list[1]['2.away_gol_yemedigi_mac_toplam'],
        "3.Away Team Member Gol Yemediği Maç Toplam": away_list[2]['3.away_gol_yemedigi_mac_toplam'],
        "4.Away Team Member Gol Yemediği Maç Toplam": away_list[3]['4.away_gol_yemedigi_mac_toplam'],
        "5.Away Team Member Gol Yemediği Maç Toplam": away_list[4]['5.away_gol_yemedigi_mac_toplam'],
        "6.Away Team Member Gol Yemediği Maç Toplam": away_list[5]['6.away_gol_yemedigi_mac_toplam'],
        "7.Away Team Member Gol Yemediği Maç Toplam": away_list[6]['7.away_gol_yemedigi_mac_toplam'],
        "8.Away Team Member Gol Yemediği Maç Toplam": away_list[7]['8.away_gol_yemedigi_mac_toplam'],
        "9.Away Team Member Gol Yemediği Maç Toplam": away_list[8]['9.away_gol_yemedigi_mac_toplam'],
        "10.Away Team Member Gol Yemediği Maç Toplam": away_list[9]['10.away_gol_yemedigi_mac_toplam'],
        "11.Away Team Member Gol Yemediği Maç Toplam": away_list[10]['11.away_gol_yemedigi_mac_toplam'],
        ##
        "1.Away Team Member Süre Toplam": away_list[0]['1.away_sure_toplam'],
        "2.Away Team Member Süre Toplam": away_list[1]['2.away_sure_toplam'],
        "3.Away Team Member Süre Toplam": away_list[2]['3.away_sure_toplam'],
        "4.Away Team Member Süre Toplam": away_list[3]['4.away_sure_toplam'],
        "5.Away Team Member Süre Toplam": away_list[4]['5.away_sure_toplam'],
        "6.Away Team Member Süre Toplam": away_list[5]['6.away_sure_toplam'],
        "7.Away Team Member Süre Toplam": away_list[6]['7.away_sure_toplam'],
        "8.Away Team Member Süre Toplam": away_list[7]['8.away_sure_toplam'],
        "9.Away Team Member Süre Toplam": away_list[8]['9.away_sure_toplam'],
        "10.Away Team Member Süre Toplam": away_list[9]['10.away_sure_toplam'],
        "11.Away Team Member Süre Toplam": away_list[10]['11.away_sure_toplam'],
        "Home Toplam Sut": home_istatistik[0],
        "Home İsabetsiz Sut": home_istatistik[1],
        "Home Kurtarıs": home_istatistik[2],
        "Home Korner": home_istatistik[3],
        "Home Serbest Vurus": home_istatistik[4],
        "Home Faul": home_istatistik[5],
        "Home Ofsayt" :home_istatistik[6],
        ##away
        "Away Toplam Sut": away_istatistik[0],
        "Away İsabetsiz Sut": away_istatistik[1],
        "Away Kurtarıs": away_istatistik[2],
        "Away Korner": away_istatistik[3],
        "Away Serbest Vurus": away_istatistik[4],
        "Away Faul": away_istatistik[5],
        "Away Ofsayt" :away_istatistik[6],
        ################### kulup_karsilastirmasi
        "Home Toplam Deger" :kulup_karsilastirmasi[0],
        "Home ø Piyasa Degeri" :kulup_karsilastirmasi[1],
        "Away Toplam Deger" :kulup_karsilastirmasi[2],
        "Away ø Piyasa Degeri" :kulup_karsilastirmasi[3],
        
        }
    
    
    # İşlemler tamamlandıktan sonra sekmeyi kapat
    driver.close()
    # Ana sekmeye geri dön
    driver.switch_to.window(ana_sekmeye_don)
    #print(match_data)
    return match_data

    
def data(url):
    try:
        all_matches = []
        driver.execute_script("window.scrollBy(0, 300);")  # 100 piksel aşağı kaydırır
        # Sayfanın yüklenmesini bekle
        wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, 'large-6'))
            )
        weeks=driver.find_elements(By.CLASS_NAME,'large-6')
        for week in weeks:
            # Satırlardaki skorlar
            rows = week.find_elements(By.XPATH, ".//td[contains(@class, 'zentriert') and contains(@class, 'hauptlink')]")
            for match in rows:
                ergebnis_link = match.find_element(By.CLASS_NAME,'ergebnis-link')
                #string olarak alınır sonra işimize yarayacak
                href_match=ergebnis_link.get_attribute("href")
                all_matches.extend(extract_data(href_match))
            time.sleep(3)
            driver.execute_script("window.scrollBy(0, 300);")  # 100 piksel aşağı kaydırır
        
        isim="Turkey(2024-2025).csv"
        df = pd.DataFrame([all_matches])
        # CSV dosyası olarak kaydet (noktalı virgül ile ayrılmış)
        df.to_csv(isim, index=False, encoding="utf-8-sig", sep=";")
        print("CSV dosyası başarıyla oluşturuldu:", isim)
    except Exception as e:
        print(e)
    

url=f"https://www.transfermarkt.com.tr/{league}/gesamtspielplan/wettbewerb/TR1?saison_id={season}&spieltagVon={start_week}&spieltagBis={end_week}"
driver.get(url)
time.sleep(2)
data(url)
driver.quit()