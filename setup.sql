-- Setup database penilaian takbiran
-- Jalankan query ini di MySQL database kamu

CREATE TABLE IF NOT EXISTS titik_lokasi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama_titik VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    role ENUM('admin', 'juri') NOT NULL DEFAULT 'juri',
    titik_id INT NULL,
    aspek ENUM('kerapian', 'kekompakan', 'keutuhan') NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (titik_id) REFERENCES titik_lokasi(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS peserta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nomor_urut INT NOT NULL,
    nama_grup VARCHAR(150) NOT NULL,
    asal VARCHAR(150) NOT NULL COMMENT 'Nama masjid/mushola',
    jumlah_anggota INT NOT NULL,
    jenis_kelamin ENUM('Laki-laki', 'Perempuan', 'Campuran') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS penilaian (
    id INT AUTO_INCREMENT PRIMARY KEY,
    peserta_id INT NOT NULL,
    titik_id INT NOT NULL,
    aspek ENUM('kerapian', 'kekompakan', 'keutuhan') NOT NULL,
    nilai INT NOT NULL CHECK (nilai IN (70,75,80,85,90,95,100)),
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_penilaian (peserta_id, titik_id, aspek),
    FOREIGN KEY (peserta_id) REFERENCES peserta(id) ON DELETE CASCADE,
    FOREIGN KEY (titik_id) REFERENCES titik_lokasi(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Akun admin default (username: admin, password: admin123)
INSERT IGNORE INTO users (nama, username, password, role) VALUES ('Administrator', 'admin', 'admin123', 'admin');
