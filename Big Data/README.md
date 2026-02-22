Goodreads Book Recommendation System with PySpark (ALS)
Bu proje, Big Data (Büyük Veri) tekniklerini kullanarak milyonlarca satırlık Goodreads veri seti üzerinde bir kitap öneri sistemi geliştirmeyi amaçlar. Proje kapsamında PySpark MLlib kütüphanesi ve Alternating Least Squares (ALS) algoritması kullanılmıştır.

🚀 Proje Özeti
Proje, kullanıcıların kitaplara verdiği puanları analiz ederek, henüz okumadıkları kitaplar için tahminler yürütür. Sadece bir öneri motoru değil, aynı zamanda büyük veri ortamında bellek yönetimi ve hiper-parametre optimizasyonu üzerine kapsamlı bir çalışmadır.

🛠️ Kullanılan Teknolojiler
Dil: Python

Platform: Apache Spark (PySpark)

Makine Öğrenmesi: Collaborative Filtering (ALS Algoritması)

Veri İşleme: Spark SQL, DataFrames

Veri Kaynağı: Goodreads Interactions & Books Metadata

📋 Öne Çıkan Özellikler
1. Büyük Veri Optimizasyonu
Veri setinin büyüklüğü (10 Milyondan fazla etkileşim) nedeniyle Spark konfigürasyonları özel olarak ayarlanmıştır:

Driver Memory: 18GB

Executor Memory: 8GB

Partitioning: Veriler user_id üzerinden 100-200 partition'a bölünerek shuffle maliyeti düşürülmüştür.

Caching & Checkpointing: Eğitim sürecini hızlandırmak ve bellek hatalarını önlemek için veri önbelleğe alınmış ve checkpoint mekanizması kullanılmıştır.

2. Model Eğitimi ve Hiper-Parametre Optimizasyonu
En iyi sonucu veren modeli bulmak için şu parametreler üzerinde Grid Search yapılmıştır:

Rank (Gizli Özellik Sayısı): [10, 50, 200]

MaxIter (İterasyon Sayısı): [10, 50, 200]

RegParam (Lambda - Regülarizasyon): [0.01, 0.1]

3. Değerlendirme Metrikleri
Model başarısı RMSE (Root Mean Squared Error) ve MSE üzerinden ölçülmüştür. Yapılan testler sonucunda en düşük RMSE değerine Rank: 200, Iteration: 50/200, Lambda: 0.1 kombinasyonu ile ulaşılmıştır.

🔍 Analiz ve Öneriler
Notebook içerisinde model eğitildikten sonra şu analizler yapılabilmektedir:

Kullanıcı Bazlı Tahmin: Belirli bir kullanıcının bir kitaba vereceği puanın tahmini.

Benzerlik Analizi: Cosine Similarity kullanılarak bir kitabı en çok beğenecek potansiyel 10 kullanıcının belirlenmesi.

Metadata Entegrasyonu: goodreads_books.json verisi ile eşleşme yapılarak kitap isimlerinin sonuçlara eklenmesi.

⚙️ Kurulum ve Çalıştırma
Spark Kurulumu: Yerel makinenizde veya bir cluster üzerinde Apache Spark'ın kurulu olduğundan emin olun.

Veri Seti: Veri setlerini (goodreads_interactions.csv ve goodreads_books.json) notebook ile aynı dizine ekleyin.

Kütüphaneler:

Bash
pip install pyspark matplotlib pandas numpy seaborn
Notebook'u Çalıştırın: als BİG DATA.ipynb dosyasını Jupyter üzerinden başlatın.

📊 Sonuçlar
Yapılan denemeler, gizli özellik sayısı (Rank) arttıkça modelin veri üzerindeki karmaşıklığı daha iyi kavradığını ve RMSE değerinin düştüğünü göstermiştir. Final modeli als_model_rank200_iter200_lambda0.1 klasörüne kaydedilmiştir.

Bu proje, bilgisayar mühendisliği eğitimim kapsamında "Büyük Veri Analizi" çalışmaları için geliştirilmiştir.