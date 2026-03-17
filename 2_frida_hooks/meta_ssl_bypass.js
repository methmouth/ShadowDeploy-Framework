// Frida completo para Meta/Facebook SSL Pinning + Objection bypass
Java.perform(function() {
    // Hook TrustManager (Java layer)
    var X509TrustManager = Java.use("javax.net.ssl.X509TrustManager");
    var TrustManagerImpl = Java.use("com.android.org.conscrypt.TrustManagerImpl");
    
    TrustManagerImpl.verifyChain.implementation = function(untrustedChain, trustAnchorChain, host, clientAuth, ocspData, tlsSctData) {
        console.log("[+] SSL Pinning bypass: TrustManagerImpl");
        return Array(1).fill(Java.use("java.security.cert.X509Certificate").$new());
    };
    
    // Native layer: libliger.so (Facebook custom HTTP)
    Interceptor.attach(Module.findExportByName("libliger.so", "tls_verify_peer_cert"), {
        onLeave: function(retval) { retval.replace(0x1); }
    });
    
    // WebView bypass
    var WebViewClient = Java.use("android.webkit.WebViewClient");
    WebViewClient.onReceivedSslError.implementation = function(view, handler, error) {
        console.log("[+] WebView SSL bypass");
        handler.proceed();
    };
});