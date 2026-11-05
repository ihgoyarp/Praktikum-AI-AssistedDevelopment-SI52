# Lab Equipment Loan System

Backend REST API untuk mengelola peminjaman alat laboratorium kampus, dibangun
dengan Python, Flask, dan SQLite sesuai `requirement.md`, `prd.md`, dan
`architecture.md`.

## Fitur

- Master alat laboratorium beserta stok total dan stok tersedia.
- Peminjaman alat dengan pengurangan stok otomatis dan atomik.
- Pengembalian alat dengan pemulihan stok dan pencegahan pengembalian ganda.
- Riwayat peminjaman berdasarkan NIM mahasiswa.

## Kebutuhan

- Python 3.x
- pip

## Instalasi

```bash
python -m venv .venv
```

Windows (Python standar):

```powershell
.venv\Scripts\activate
```

Linux/macOS, atau MSYS2/UCRT64 di Windows (venv memakai folder `bin/`):

```bash
source .venv/bin/activate
```

Pasang dependency:

```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```bash
python run.py
```

Aplikasi tersedia di `http://127.0.0.1:5000`.

Database SQLite dibuat otomatis di `instance/lab_equipment.db` saat aplikasi
pertama kali dijalankan. Lokasi database dapat diubah melalui environment
variable `LAB_DATABASE`, misalnya:

```powershell
$env:LAB_DATABASE = "C:\data\lab_equipment.db"
python run.py
```

## Endpoint

| Method | Endpoint | Deskripsi | Sukses |
|---|---|---|---|
| GET | `/items` | Daftar alat dan stok terkini | 200 |
| POST | `/items` | Tambah master alat | 201 |
| POST | `/loans` | Ajukan peminjaman | 201 |
| PUT | `/loans/{id}/return` | Kembalikan alat | 200 |
| GET | `/loans/student/{student_id}` | Riwayat peminjaman per NIM | 200 |

### Contoh request

Tambah alat:

```json
POST /items
{
  "name": "Multimeter",
  "total_stock": 10
}
```

`available_stock` otomatis diisi sama dengan `total_stock`.

Ajukan peminjaman:

```json
POST /loans
{
  "student_id": "20240001",
  "item_id": 1,
  "quantity": 2
}
```

Kembalikan alat (tanpa body):

```text
PUT /loans/1/return
```

### Format error

```json
{
  "error": "Insufficient stock"
}
```

Status code yang digunakan:

- `400 Bad Request` untuk input tidak valid, stok tidak mencukupi, atau
  pengembalian transaksi yang sudah `RETURNED`.
- `404 Not Found` untuk item atau transaksi yang tidak ditemukan.
- `201 Created` untuk pembuatan item atau peminjaman.
- `200 OK` untuk GET dan pengembalian yang berhasil.

## Pengujian

```bash
pytest
```

Test menggunakan database SQLite sementara sehingga tidak mengubah database
aplikasi.

## Aturan Bisnis

- Stok berkurang otomatis saat peminjaman berhasil dicatat.
- Peminjaman ditolak (400) jika `available_stock - quantity < 0`.
- Peminjaman ditolak (404) jika `item_id` tidak ada.
- Pengembalian memulihkan stok sesuai `quantity` dan mengubah status menjadi
  `RETURNED`.
- Transaksi `RETURNED` tidak dapat dikembalikan dua kali (400).
- Perubahan stok dan transaksi dijalankan dalam satu transaksi database.

## Batasan

Sesuai `architecture.md`, hal berikut belum termasuk dalam ruang lingkup:

- Autentikasi dan otorisasi.
- Endpoint ubah/hapus master alat.
- Proses pembatalan transaksi (`CANCELLED`).
- Batas maksimum pinjaman, jatuh tempo, dan denda.
- Pagination, pencarian, dan pengurutan.
- Konfigurasi deployment production.
