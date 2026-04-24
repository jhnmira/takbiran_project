from flask import Flask, render_template, request, redirect, session, url_for, flash
import mysql.connector
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "takbiran2025secret")

DB_CONFIG = {
    "host": os.environ.get("MYSQLHOST"),
    "user": os.environ.get("MYSQLUSER"),
    "password": os.environ.get("MYSQLPASSWORD"),
    "database": os.environ.get("MYSQLDATABASE"),
    "port": int(os.environ.get("MYSQLPORT", 3306)),
    "connection_timeout": 10,
    "use_pure": True
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Akses ditolak. Hanya admin yang bisa mengakses halaman ini.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

# ===================== AUTH =====================

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            cursor.close()
            db.close()
            if user:
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['role'] = user['role']
                session['nama'] = user['nama']
                if user['role'] == 'juri':
                    session['titik_id'] = user['titik_id']
                    session['aspek'] = user['aspek']
                return redirect(url_for('dashboard'))
            else:
                flash('Username atau password salah!', 'error')
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ===================== DASHBOARD =====================

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total FROM peserta")
        total_peserta = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM penilaian")
        total_nilai = cursor.fetchone()['total']
        cursor.execute("SELECT COUNT(*) as total FROM titik_lokasi")
        total_titik = cursor.fetchone()['total']
        cursor.close()
        db.close()
        return render_template('dashboard.html', total_peserta=total_peserta, total_nilai=total_nilai, total_titik=total_titik)
    except Exception as e:
        return f"Error: {e}", 500

# ===================== PESERTA (ADMIN) =====================

@app.route('/peserta')
@admin_required
def peserta():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM peserta ORDER BY nama_grup")
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('peserta.html', data=data)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/peserta/tambah', methods=['GET', 'POST'])
@admin_required
def tambah_peserta():
    if request.method == 'POST':
        nama_grup = request.form['nama_grup']
        asal = request.form['asal']
        jumlah = request.form['jumlah']
        jenis_kelamin = request.form['jenis_kelamin']
        nomor_urut = request.form['nomor_urut']
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO peserta (nama_grup, asal, jumlah_anggota, jenis_kelamin, nomor_urut) VALUES (%s,%s,%s,%s,%s)",
                (nama_grup, asal, jumlah, jenis_kelamin, nomor_urut)
            )
            db.commit()
            cursor.close()
            db.close()
            flash('Peserta berhasil ditambahkan!', 'success')
            return redirect(url_for('peserta'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('form_peserta.html', data=None)

@app.route('/peserta/edit/<int:id>', methods=['GET', 'POST'])
@admin_required
def edit_peserta(id):
    db = get_db()
    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        nama_grup = request.form['nama_grup']
        asal = request.form['asal']
        jumlah = request.form['jumlah']
        jenis_kelamin = request.form['jenis_kelamin']
        nomor_urut = request.form['nomor_urut']
        cursor.execute(
            "UPDATE peserta SET nama_grup=%s, asal=%s, jumlah_anggota=%s, jenis_kelamin=%s, nomor_urut=%s WHERE id=%s",
            (nama_grup, asal, jumlah, jenis_kelamin, nomor_urut, id)
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Peserta berhasil diupdate!', 'success')
        return redirect(url_for('peserta'))
    cursor.execute("SELECT * FROM peserta WHERE id=%s", (id,))
    data = cursor.fetchone()
    cursor.close()
    db.close()
    return render_template('form_peserta.html', data=data)

@app.route('/peserta/hapus/<int:id>')
@admin_required
def hapus_peserta(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM peserta WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Peserta berhasil dihapus!', 'success')
    return redirect(url_for('peserta'))

# ===================== TITIK LOKASI (ADMIN) =====================

@app.route('/titik')
@admin_required
def titik():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM titik_lokasi ORDER BY nama_titik")
        data = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('titik.html', data=data)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/titik/tambah', methods=['POST'])
@admin_required
def tambah_titik():
    nama_titik = request.form['nama_titik']
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO titik_lokasi (nama_titik) VALUES (%s)", (nama_titik,))
    db.commit()
    cursor.close()
    db.close()
    flash('Titik lokasi berhasil ditambahkan!', 'success')
    return redirect(url_for('titik'))

@app.route('/titik/hapus/<int:id>')
@admin_required
def hapus_titik(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM titik_lokasi WHERE id=%s", (id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Titik lokasi berhasil dihapus!', 'success')
    return redirect(url_for('titik'))

# ===================== KELOLA JURI (ADMIN) =====================

@app.route('/kelola-juri')
@admin_required
def kelola_juri():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT u.*, t.nama_titik FROM users u
            LEFT JOIN titik_lokasi t ON u.titik_id = t.id
            WHERE u.role = 'juri' ORDER BY u.nama
        """)
        data = cursor.fetchall()
        cursor.execute("SELECT * FROM titik_lokasi ORDER BY nama_titik")
        titik_list = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('kelola_juri.html', data=data, titik_list=titik_list)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/kelola-juri/tambah', methods=['POST'])
@admin_required
def tambah_juri():
    nama = request.form['nama']
    username = request.form['username']
    password = request.form['password']
    titik_id = request.form['titik_id']
    aspek = request.form['aspek']
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO users (nama, username, password, role, titik_id, aspek) VALUES (%s,%s,%s,'juri',%s,%s)",
            (nama, username, password, titik_id, aspek)
        )
        db.commit()
        cursor.close()
        db.close()
        flash('Akun juri berhasil ditambahkan!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('kelola_juri'))

@app.route('/kelola-juri/hapus/<int:id>')
@admin_required
def hapus_juri(id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM users WHERE id=%s AND role='juri'", (id,))
    db.commit()
    cursor.close()
    db.close()
    flash('Akun juri berhasil dihapus!', 'success')
    return redirect(url_for('kelola_juri'))

# ===================== INPUT NILAI (JURI) =====================

@app.route('/input-nilai')
@login_required
def input_nilai():
    if session.get('role') not in ['juri', 'admin']:
        return redirect(url_for('dashboard'))
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM peserta ORDER BY nomor_urut")
        peserta_list = cursor.fetchall()

        titik_id = session.get('titik_id')
        aspek = session.get('aspek')

        if session.get('role') == 'admin':
            cursor.execute("SELECT * FROM penilaian ORDER BY peserta_id")
        else:
            cursor.execute(
                "SELECT * FROM penilaian WHERE titik_id=%s AND aspek=%s",
                (titik_id, aspek)
            )
        nilai_existing = {(r['peserta_id'], r['titik_id'], r['aspek']): r['nilai'] for r in cursor.fetchall()}
        cursor.close()
        db.close()
        return render_template('input_nilai.html', peserta_list=peserta_list, nilai_existing=nilai_existing, titik_id=titik_id, aspek=aspek)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/input-nilai/simpan', methods=['POST'])
@login_required
def simpan_nilai():
    if session.get('role') not in ['juri', 'admin']:
        return redirect(url_for('dashboard'))
    titik_id = session.get('titik_id')
    aspek = session.get('aspek')
    user_id = session.get('user_id')
    try:
        db = get_db()
        cursor = db.cursor()
        for key, value in request.form.items():
            if key.startswith('nilai_'):
                peserta_id = int(key.split('_')[1])
                nilai = int(value)
                cursor.execute("""
                    INSERT INTO penilaian (peserta_id, titik_id, aspek, nilai, user_id)
                    VALUES (%s,%s,%s,%s,%s)
                    ON DUPLICATE KEY UPDATE nilai=%s, user_id=%s
                """, (peserta_id, titik_id, aspek, nilai, user_id, nilai, user_id))
        db.commit()
        cursor.close()
        db.close()
        flash('Nilai berhasil disimpan!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('input_nilai'))

# ===================== REKAP NILAI =====================

@app.route('/rekap')
@login_required
def rekap():
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id, p.nama_grup, p.asal, p.nomor_urut, p.jenis_kelamin, p.jumlah_anggota,
                COALESCE(SUM(CASE WHEN pn.aspek='kerapian' THEN pn.nilai END), 0) as total_kerapian,
                COALESCE(SUM(CASE WHEN pn.aspek='kekompakan' THEN pn.nilai END), 0) as total_kekompakan,
                COALESCE(SUM(CASE WHEN pn.aspek='keutuhan' THEN pn.nilai END), 0) as total_keutuhan,
                COALESCE(SUM(pn.nilai), 0) as total_nilai
            FROM peserta p
            LEFT JOIN penilaian pn ON p.id = pn.peserta_id
            GROUP BY p.id
            ORDER BY total_nilai DESC
        """)
        rekap_data = cursor.fetchall()

        cursor.execute("""
            SELECT t.nama_titik, p.nama_grup, pn.aspek, pn.nilai
            FROM penilaian pn
            JOIN peserta p ON pn.peserta_id = p.id
            JOIN titik_lokasi t ON pn.titik_id = t.id
            ORDER BY t.nama_titik, p.nomor_urut
        """)
        detail_data = cursor.fetchall()
        cursor.close()
        db.close()
        return render_template('rekap.html', rekap_data=rekap_data, detail_data=detail_data)
    except Exception as e:
        return f"Error: {e}", 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
