# AI-Hoshino

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <h3 align="center">Weekly Class Scheduling Solver using Local Search</h3>

  <p align="center">
    An intelligent scheduling system implementation using local search algorithms
    <br />
    IF3170 - Artificial Intelligence
    <br />
    <a href="https://github.com/Darsua/AI-Hoshino"><strong>Explore the repository »</strong></a>
    <br />
    <br />
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
        <li><a href="#key-features">Key Features</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#algorithms">Algorithms</a></li>
    <li><a href="#objective-function">Objective Function</a></li>
    <li><a href="#project-structure">Project Structure</a></li>
    <li><a href="#experiments">Experiments</a></li>
    <li><a href="#team">Team</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

## About The Project

AI-Hoshino adalah sistem penjadwalan kelas mingguan yang menggunakan algoritma local search untuk mengoptimalkan alokasi mata kuliah ke ruangan dan waktu. Proyek ini dikembangkan sebagai bagian dari mata kuliah IF3170 Inteligensi Artifisial di ITB.

Sistem ini menangani permasalahan penjadwalan yang kompleks dengan mempertimbangkan berbagai constraint seperti:
* Konflik waktu mahasiswa
* Kapasitas ruangan
* Konflik penggunaan ruangan
* Prioritas mata kuliah mahasiswa

### Tujuan Utama:
* Mengimplementasikan berbagai algoritma local search untuk menyelesaikan masalah scheduling
* Membandingkan performa algoritma Hill-Climbing, Simulated Annealing, dan Genetic Algorithm
* Menganalisis pengaruh parameter terhadap kualitas solusi yang dihasilkan
* Menyediakan visualisasi interaktif untuk hasil scheduling dan eksperimen

### Built With

* **Python 3.12+** - Bahasa pemrograman utama
* **Tkinter** - GUI framework
* **Matplotlib** - Visualisasi data dan grafik eksperimen
* **NumPy** - Komputasi numerik

### Key Features

**Multi-Algorithm Support**
- 4 varian Hill-Climbing (Steepest Ascent, Stochastic, Sideways Move, Random Restart)
- Simulated Annealing dengan temperature scheduling
- Genetic Algorithm dengan crossover dan mutation

**Flexible Objective Function**
- Student time conflict penalty
- Room conflict penalty dengan priority weighting
- Room capacity penalty

**Interactive GUI**
- Load dataset dari file JSON
- Konfigurasi parameter algoritma
- Visualisasi hasil scheduling dalam bentuk tabel
- Plot performa algoritma real-time

**Comprehensive CLI**
- Batch processing untuk eksperimen
- Export hasil ke file
- Progress tracking dengan iterasi dan durasi

## Getting Started

Ikuti instruksi berikut untuk menjalankan AI-Hoshino di komputer lokal Anda.

### Prerequisites

* Python 3.12 atau lebih tinggi
  ```sh
  # Cek versi Python Anda
  python --version
  ```

* uv (package installer untuk Python) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
  ```sh
  # Cek versi uv Anda
  uv --version
  ```

### Installation

1. Clone repository
   ```sh
   git clone https://github.com/Darsua/AI-Hoshino.git
   ```

2. Masuk ke direktori proyek
   ```sh
   cd AI-Hoshino
   ```

3. Install dependencies menggunakan uv
   ```sh
   uv sync
   ```

## Usage

### Running the GUI

Untuk menjalankan aplikasi dengan antarmuka grafis:

```sh
uv run python src/main.py --gui
```

### Running CLI Mode

#### Hill-Climbing (Steepest Ascent)
```sh
uv run python src/main.py test/makima.json --hc --hc-variant steepest_ascent --hc-max-iterations 1000
```

#### Hill-Climbing (Stochastic)
```sh
uv run python src/main.py test/makima.json --hc --hc-variant stochastic --hc-max-iterations 1000
```

#### Hill-Climbing (Sideways Move)
```sh
uv run python src/main.py test/makima.json --hc --hc-variant sideways_move \
  --max-sideways-moves 100 --hc-max-iterations 1000
```

#### Hill-Climbing (Random Restart)
```sh
uv run python src/main.py test/makima.json --hc --hc-variant random_restart \
  --max-restarts 10 --hc-restart-variant steepest_ascent
```

#### Simulated Annealing
```sh
uv run python src/main.py test/makima.json --sa \
  --initial-temp 500 --cooling-rate 0.97 --max-iterations 5000 --plot
```

#### Genetic Algorithm
```sh
uv run python src/main.py test/makima.json --genetic \
  --population 50 --generations 100 --plot
```

### Input Format

File input menggunakan format JSON dengan struktur sebagai berikut:

```json
{
  "kelas_mata_kuliah": [
    {
      "kode": "IF3170_K01",
      "jumlah_mahasiswa": 60,
      "sks": 3
    }
  ],
  "ruangan": [
    {
      "kode": "7609",
      "kuota": 60
    }
  ],
  "mahasiswa": [
    {
      "nim": "13523009",
      "daftar_mk": ["IF3170_K01", "IF3110_K02"],
      "prioritas": [1, 2]
    }
  ]
}
```

**Contoh dataset tersedia di folder `test/`:**
- `makima.json` - Dataset dengan 19 kelas, 10 ruangan, 255 mahasiswa
- `power.json` - Dataset dengan 18 kelas, 1 ruangan, 305 mahasiswa  
- `reze.json` - Dataset dengan 7 kelas, 6 ruangan, 180 mahasiswa

### Output Format

Program menghasilkan jadwal dalam bentuk tabel per ruangan:

```
Kode ruang: 7609
   Senin      Selasa     Rabu       Kamis      Jumat
7  IF3170_K01 IF3130_K01 IF3110_K02 IF3140_K01 IF3071_K01
8  IF3170_K01 IF3130_K01 IF3110_K02 IF3140_K01 IF3071_K01
9  IF3170_K01            IF3110_K02            IF3071_K01
...
```

## Algorithms

### 1. Hill-Climbing

Algoritma yang bergerak ke neighbor dengan nilai objective function terbaik.

**Varian yang diimplementasikan:**
- **Steepest Ascent**: Memilih neighbor terbaik dari semua kemungkinan
- **Stochastic**: Memilih neighbor secara random yang lebih baik
- **Sideways Move**: Mengizinkan perpindahan ke neighbor dengan nilai sama
- **Random Restart**: Restart dari state random ketika stuck di local optima

### 2. Simulated Annealing

Algoritma yang menggunakan konsep temperature untuk menghindari local optima dengan probabilitas penerimaan solusi yang lebih buruk.

**Fitur:**
- Temperature scheduling dengan cooling rate
- Probabilitas acceptance: e^(ΔE/T)
- Deteksi local optima otomatis
- Visualisasi acceptance probability vs iterasi

### 3. Genetic Algorithm

Algoritma evolusioner yang menggunakan populasi solusi dan operasi genetik.

**Operasi genetik:**
- **Selection**: Tournament selection
- **Crossover**: Order-based crossover dengan preserve meeting integrity
- **Mutation**: Swap meeting atau move ke slot kosong

**Parameter yang dapat dikonfigurasi:**
- Population size
- Number of generations
- Crossover rate
- Mutation rate

## Team

**Kelompok: AI_Hoshino**

| Nama | NIM | Tugas |
|------|-----|-------|
| Muhammad Hazim Ramadan Prajoda | 13523009 | Implementasi Simulated Annealing, Penanggung Jawab Laporan, GUI |
| Faqih Muhammad Syuhada | 13523057 | Implementasi Hill-Climbing (4 varian), Penulisan Laporan |
| Darrel Adinarya Sunanda | 13523061 | Desain Objective Function, Implementasi Genetic Algorithm |

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Acknowledgments

* [Russell & Norvig - Artificial Intelligence: A Modern Approach](http://aima.cs.berkeley.edu/)
* [GeeksforGeeks - Simulated Annealing](https://www.geeksforgeeks.org/artificial-intelligence/what-is-simulated-annealing/)
* [Introduction to Genetic Algorithms](https://www.geeksforgeeks.org/genetic-algorithms/)
* Staf Pengajar IF3170 - STEI ITB
* Asisten Lab AI'22

---

<div align="center">
  <p>
    <strong>IF3170 - Inteligensi Artifisial</strong><br>
    Sekolah Teknik Elektro dan Informatika<br>
    Institut Teknologi Bandung<br>
    Semester II Tahun 2024/2025
  </p>
</div>
