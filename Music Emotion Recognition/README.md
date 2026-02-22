
# Acoustic Music Classification Pipeline (Happy, Sad, Angry, Relax)

dataset: https://archive.ics.uci.edu/dataset/862/turkish+music+emotion

Bu proje, müzik parçalarının akustik özelliklerini kullanarak onları dört farklı duygu durumuna (**Happy, Sad, Angry, Relax**) göre sınıflandıran kapsamlı bir makine öğrenmesi boru hattıdır (pipeline). R dili ve `tidymodels` ekosistemi kullanılarak geliştirilmiştir.

## 🎵 Proje Hakkında

Projenin temel amacı, bir şarkının teknik özelliklerinden yola çıkarak hissettirdiği duyguyu tahmin etmektir. `Acoustic Features.csv` veri seti üzerinde gerçekleştirilen bu çalışma, veri temizlemeden model seçimine ve başarı metriklerinin raporlanmasına kadar uçtan uca bir süreç sunar.

### Kullanılan Teknolojiler ve Kütüphaneler

* **Dil:** R
* **Ekosistem:** `tidymodels` (rsample, recipes, parsnip, tune, yardstick)
* **Modelleme:** `glmnet`, `ranger`, `xgboost`, `MASS`, `LiblineaR`
* **Görselleştirme:** `ggplot2`, `vip`

## 🛠 Makine Öğrenmesi Pipeline Süreci

Kod bloğu şu aşamaları otomatik olarak gerçekleştirir:

1. **Veri Keşfi ve Ön İşleme:** Eksik değerlerin (NA) tespiti, medyan ile imputasyon, değişkenlerin normalizasyonu ve düşük varyanslı (NZV) özniteliklerin elenmesi.
2. **Öznitelik Seçimi (Feature Selection):** Multinomial **LASSO Regression** kullanılarak model için en anlamlı değişkenler seçilir ve katsayı analizleri yapılır.
3. **Model Eğitimi:** Beş farklı algoritma (Elastic Net, Linear SVM, Random Forest, LDA ve XGBoost) eğitilir.
4. **Hiper-parametre Optimizasyonu:** `tune_grid` kullanılarak modellerin en iyi parametreleri (penalty, mixture, cost, mtry, vb.) 5-fold Cross-Validation ile belirlenir.
5. **Değerlendirme Stratejileri:**
* **Three-way Split (60/20/20):** Model seçimi ve nihai test için ana yöntem.
* **Holdout (80/20):** Klasik eğitim-test ayrımı.
* **5-Fold CV:** Modelin kararlılığını (stability) ölçmek için tüm veri setinde çapraz doğrulama.



## 📊 Modeller

| Model | Algoritma / Engine | Özellik |
| --- | --- | --- |
| **Elastic Net** | `glmnet` | Multinomial Lojistik Regresyon |
| **Linear SVM** | `LiblineaR` | Yüksek boyutlu verilerde güçlü sınıflandırma |
| **Random Forest** | `ranger` | Karar ağacı tabanlı topluluk öğrenmesi |
| **LDA** | `MASS` | Lineer Diskriminant Analizi |
| **XGBoost** | `xgboost` | Gradyan artırma (Gradient Boosting) |

## 📁 Çıktılar (Artifacts)

Kod çalıştıktan sonra `artifacts_report` klasörü altında şu sonuçları üretir:

* **FIG_correlation_matrix.png:** Değişkenler arası ilişki haritası.
* **FIG_feature_selection_lasso_top20.png:** LASSO tarafından seçilen en önemli 20 değişken.
* **FIG_rf_importance_top20.png:** Random Forest modelinin öznitelik önem sıralaması.
* **TABLE_model_comparison_all_evals.csv:** Tüm modellerin Accuracy, Precision, Recall ve F1-Macro skorlarını içeren karşılaştırma tablosu.
* **Saved Models (.rds):** Eğitilmiş en iyi modellerin kaydedilmiş halleri.

## 🚀 Çalıştırma Talimatları

1. RStudio'yu açın.
2. `Acoustic Features.csv` dosyasının script ile aynı dizinde olduğundan emin olun.
3. Gerekli kütüphaneleri yükleyin:
```r
install.packages(c("tidymodels", "readr", "vip", "glmnet", "xgboost", "LiblineaR", "MASS"))

```


4. `music_project.R` dosyasını çalıştırın.

---

