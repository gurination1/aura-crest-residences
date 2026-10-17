/**
 * Aura Crest - Botanical Lotus Revolution Kinematic Engine
 * Continuous idle revolution coupled with Lenis smooth scroll velocity & instant direction reversal.
 * Exactly mirrors the header revolving seal kinematics:
 * - Downward scroll -> accelerates rotation in forward direction
 * - Upward scroll -> immediately reverses rotation direction & accelerates
 * - Damping -> decelerates back to calm idle revolution in current direction
 */
(function() {
  'use strict';

  function initLotusKinematics() {
    const clusters = document.querySelectorAll('.lotus-cluster');
    if (!clusters.length) return;

    // Collect all individual lotus items with distinct speeds, phases, and base multipliers
    const lotuses = [];
    clusters.forEach((cluster, cIdx) => {
      const items = cluster.querySelectorAll('.lotus-item');
      items.forEach((item, iIdx) => {
        const speedAttr = parseFloat(item.getAttribute('data-speed')) || (iIdx % 2 === 0 ? 1.0 : -1.0);
        // Base rotational speed in degrees per second (idle spin)
        const baseSpeed = 22.0 * speedAttr;
        
        lotuses.push({
          el: item,
          angle: (cIdx * 43 + iIdx * 67) % 360,
          baseSpeed: baseSpeed
        });
      });
    });

    // Shared kinematic speed multiplier state
    const kinematic = {
      speedMultiplier: 1.0
    };

    let currentDir = 1;
    let dampenTimeout = null;

    // Core scroll velocity handler
    function handleVelocity(vel) {
      if (Math.abs(vel) < 0.04) return;

      // Positive velocity = scrolling down; Negative velocity = scrolling up
      currentDir = vel > 0 ? 1 : -1;

      // Dynamic acceleration proportional to scroll velocity
      const boost = 1.0 + Math.min(Math.abs(vel) * 0.16, 4.2);
      const target = currentDir * boost;

      // GSAP smooth tween to boosted speed
      if (window.gsap) {
        gsap.to(kinematic, {
          speedMultiplier: target,
          duration: 0.28,
          ease: "power2.out",
          overwrite: true
        });

        // Clear any prior dampen timer
        clearTimeout(dampenTimeout);

        // Gracefully decelerate back to idle speed in the current direction
        dampenTimeout = setTimeout(() => {
          gsap.to(kinematic, {
            speedMultiplier: currentDir * 1.0,
            duration: 1.2,
            ease: "power2.out"
          });
        }, 80);
      } else {
        kinematic.speedMultiplier = target;
      }
    }

    // Connect to Lenis instance (polling until ready to ensure attachment after preloader)
    function attachToLenis() {
      if (window.lenis && typeof window.lenis.on === 'function') {
        window.lenis.on('scroll', (e) => {
          if (e && typeof e.velocity === 'number') {
            handleVelocity(e.velocity);
          }
        });
        return true;
      }
      return false;
    }

    if (!attachToLenis()) {
      const lenisCheckInterval = setInterval(() => {
        if (attachToLenis()) {
          clearInterval(lenisCheckInterval);
        }
      }, 100);
      setTimeout(() => clearInterval(lenisCheckInterval), 15000);
    }

    // Native wheel & touch fallback listeners for instantaneous responsiveness
    window.addEventListener('wheel', (e) => {
      if (typeof e.deltaY === 'number') {
        handleVelocity(e.deltaY * 0.12);
      }
    }, { passive: true });

    let touchStartY = 0;
    window.addEventListener('touchstart', (e) => {
      if (e.touches && e.touches[0]) {
        touchStartY = e.touches[0].clientY;
      }
    }, { passive: true });

    window.addEventListener('touchmove', (e) => {
      if (e.touches && e.touches[0]) {
        const delta = touchStartY - e.touches[0].clientY;
        touchStartY = e.touches[0].clientY;
        handleVelocity(delta * 0.25);
      }
    }, { passive: true });

    // GSAP Ticker loop for silky 120fps animation
    function updateFrame(deltaMs) {
      const dt = Math.min(deltaMs, 100) / 1000;
      for (let i = 0; i < lotuses.length; i++) {
        const lotus = lotuses[i];
        lotus.angle = (lotus.angle + lotus.baseSpeed * kinematic.speedMultiplier * dt) % 360;
        lotus.el.style.transform = 'rotate(' + lotus.angle.toFixed(2) + 'deg)';
      }
    }

    if (window.gsap && gsap.ticker) {
      gsap.ticker.add((time, delta) => updateFrame(delta));
    } else {
      let lastTime = performance.now();
      function rafLoop(now) {
        const dt = now - lastTime;
        lastTime = now;
        updateFrame(dt);
        requestAnimationFrame(rafLoop);
      }
      requestAnimationFrame(rafLoop);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLotusKinematics);
  } else {
    initLotusKinematics();
  }
})();
