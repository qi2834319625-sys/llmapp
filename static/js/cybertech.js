/* ===== Particle Background Animation ===== */
(function() {
  var canvas = document.getElementById('particle-canvas');
  if (!canvas) return;
  var ctx = canvas.getContext('2d');
  var particles = [];
  var mouse = { x: -1000, y: -1000 };
  
  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  resize();
  window.addEventListener('resize', resize);
  window.addEventListener('mousemove', function(e) { mouse.x = e.clientX; mouse.y = e.clientY; });
  window.addEventListener('touchmove', function(e) { mouse.x = e.touches[0].clientX; mouse.y = e.touches[0].clientY; });
  
  var colors = ['#00f5ff', '#ff00e5', '#39ff14', '#b026ff', '#ff6b00'];
  
  function createParticle() {
    return {
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.5,
      vy: (Math.random() - 0.5) * 0.5,
      size: Math.random() * 2 + 0.5,
      color: colors[Math.floor(Math.random() * colors.length)],
      alpha: Math.random() * 0.5 + 0.1,
    };
  }
  
  for (var i = 0; i < 80; i++) particles.push(createParticle());
  
  function animate() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    for (var i = 0; i < particles.length; i++) {
      var p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;
      
      // Mouse interaction
      var dx = mouse.x - p.x;
      var dy = mouse.y - p.y;
      var dist = Math.sqrt(dx*dx + dy*dy);
      if (dist < 150) {
        p.vx -= dx * 0.00005;
        p.vy -= dy * 0.00005;
      }
      
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.globalAlpha = p.alpha;
      ctx.fill();
    }
    
    // Draw connections
    ctx.globalAlpha = 0.08;
    ctx.strokeStyle = '#00f5ff';
    ctx.lineWidth = 0.5;
    for (var i = 0; i < particles.length; i++) {
      for (var j = i + 1; j < particles.length; j++) {
        var dx = particles[i].x - particles[j].x;
        var dy = particles[i].y - particles[j].y;
        var dist = Math.sqrt(dx*dx + dy*dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.globalAlpha = 0.08 * (1 - dist / 120);
          ctx.stroke();
        }
      }
    }
    ctx.globalAlpha = 1;
    
    requestAnimationFrame(animate);
  }
  animate();
})();

/* ===== Global Toast ===== */
window.showToast = function(msg, type, duration) {
  type = type || 'info';
  duration = duration || 4000;
  var container = document.getElementById('toastContainer');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }
  var icons = { success:'✅', info:'ℹ️', warning:'⚠️', error:'❌' };
  var toast = document.createElement('div');
  toast.className = 'toast toast-' + type;
  toast.innerHTML = '<span style="font-size:1.2em;">' + (icons[type]||'ℹ️') + '</span><span style="flex:1;font-size:0.88em;">' + msg + '</span><span style="cursor:pointer;opacity:0.5;" onclick="this.parentElement.remove()">×</span>';
  container.appendChild(toast);
  setTimeout(function() { if (toast.parentElement) toast.remove(); }, duration);
};

/* ===== Nav Back Button ===== */
(function() {
  var nav = document.getElementById('navBack');
  if (nav && window.location.pathname !== '/dashboard' && window.location.pathname !== '/') {
    nav.style.display = 'inline-flex';
  }
})();
