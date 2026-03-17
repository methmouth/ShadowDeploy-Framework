#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🕷️ ShadowDeploy-Framework: Setup Automático..."

# Paquetes Termux
pkg update -y && pkg install python git aapt dx openjdk-17 apksigner mitmproxy frida-tools adb termux-api -y
termux-setup-storage

# Estructura de carpetas
mkdir -p ShadowDeploy-Framework/{1_mitm_injector/payloads,2_frida_hooks,3_c2_server/{templates,static,payloads,logs},4_dropper_app/{src/com/pentest/dropper,res/xml}}
cd ShadowDeploy-Framework

echo "✅ Estructura creada. Copia los archivos de código ahora."
echo "Ejecuta: bash 4_dropper_app/build_termux.sh && python3 3_c2_server/server.py"