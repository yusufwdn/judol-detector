# Diagram

Berkas sumber diagram ada di `diagram/` dalam format draw.io, bisa dibuka di
[app.diagrams.net](https://app.diagrams.net) atau ekstensi draw.io untuk VS
Code. Sebagian sudah diekspor ke PNG dengan nama yang sama.

Beberapa diagram punya dua revisi. Versi bertanda `_v2` atau `_new` adalah
yang terbaru. Versi sebelumnya dipertahankan karena sebagian di antaranya
sudah diekspor ke PNG sementara revisinya belum.

## Alur sistem

| Berkas | Isi |
|---|---|
| `training_pipeline_v2.drawio` | Alur pelatihan, dari pengumpulan data sampai artefak model. Revisi terbaru |
| `training_pipeline.drawio` | Revisi sebelumnya |
| `inference_pipeline.drawio` | Alur prediksi saat sistem dipakai |
| `arsitektur_komponen.drawio` | Hubungan antar komponen: scraper, server, ekstensi |
| `waterfall_diagram.drawio` | Tahapan metode pengembangan |

Perbedaan antara alur pelatihan dan alur prediksi penting diperhatikan.
Keduanya memakai modul normalisasi yang sama, dan itu bukan kebetulan,
melainkan syarat konsistensi yang dijelaskan di
[arsitektur.md](arsitektur.md#kenapa-normalisasi-dilakukan-di-python).

## UML

| Berkas | Isi |
|---|---|
| `use_case_diagram.drawio` | Use case, dengan ekspor PNG |
| `use_case_diagram_new.drawio.png` | Revisi terbaru, hanya tersedia sebagai PNG |
| `activity_diagram_v2.drawio` | Activity diagram, revisi terbaru |
| `activity_diagram.drawio` | Revisi sebelumnya, punya ekspor PNG |
| `sequence_diagram_v2.drawio` | Sequence diagram, revisi terbaru |
| `sequence_diagram.drawio` | Revisi sebelumnya |

Dua revisi use case tambahan tersimpan di `reports/usecase_diagram_revisi.png`
dan `reports/usecase_diagram_revisi_v2.png`.

## Antarmuka

| Berkas | Isi |
|---|---|
| `popup.drawio` | Rancangan panel pengaturan ekstensi |
| `youtube-wireframe-v1.drawio` | Wireframe tampilan komentar YouTube |
| `struktur_organisasi_youtube.drawio` | Struktur elemen DOM komentar YouTube |

## Grafik hasil evaluasi

Berbeda dari diagram di atas, berkas berikut dihasilkan otomatis oleh skrip
dan ditimpa setiap kali skripnya dijalankan ulang.

| Berkas | Dihasilkan oleh |
|---|---|
| `reports/confusion_matrix_svm.png` | `src/train.py` |
| `reports/confusion_matrix_logistic_regression.png` | `src/compare_baselines.py` |
| `reports/confusion_matrix_naive_bayes_multinomialnb.png` | `src/compare_baselines.py` |
| `reports/cv_5fold_scores.png` | `src/train.py` |
| `reports/gridsearch_c_sweep.png` | `src/train.py` |
| `reports/top_features.png` | `src/inspect_features.py` |
| `reports/experiment_stemming_cv.png` | `src/experiment_stemming.py` |
| `reports/experiment_features.png` | `src/experiment_features.py` |

## Tangkapan layar

`reports/screenshots-store/store-ready/` berisi tangkapan layar yang sudah
disesuaikan ukurannya untuk Chrome Web Store. Skrip pembuatnya ada di folder
yang sama.
