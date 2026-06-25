from flask import Flask, render_template, request, Response
import subprocess
import json
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search')
def search():
    username = request.args.get('username')
    if not username:
        return {"error": "username is required"}, 400

    def generate():
        # Menjalankan perintah sherlock. Gunakan env=os.environ untuk memastikan script berjalan di environment saat ini (venv).
        # Tambahkan --print-found agar hanya mencetak yang ditemukan.
        # Jika sherlock sudah terinstall di .venv, kita bisa memanggil `sherlock`. 
        # Untuk lebih aman, jalankan dengan "python -m sherlock_project" atau langsung executable "sherlock"
        
        command = ['sherlock', username]
        
        yield f"data: {json.dumps({'status': 'info', 'message': f'Memulai pencarian untuk {username}...'})}\n\n"
        
        try:
            # Gunakan subprocess.Popen untuk streaming output
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1 # Line buffered
            )
            
            for line in iter(process.stdout.readline, ''):
                line = line.strip()
                if not line:
                    continue
                    
                # Format output sherlock: "[+] Site: https://..."
                if line.startswith('[+]'):
                    # Contoh: "[+] GitHub: https://github.com/barrukurniawan"
                    parts = line[4:].split(':', 1)
                    if len(parts) == 2:
                        site = parts[0].strip()
                        url = parts[1].strip()
                        yield f"data: {json.dumps({'status': 'found', 'site': site, 'url': url})}\n\n"
                elif line.startswith('[*]'):
                    # Info line
                    yield f"data: {json.dumps({'status': 'info', 'message': line})}\n\n"

            process.stdout.close()
            process.wait()
            
            yield f"data: {json.dumps({'status': 'done'})}\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
    # Run application
    app.run(host='0.0.0.0', debug=True, port=9900)
