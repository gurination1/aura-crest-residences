/**
 * 1:1 Implementation of ReGGae Canvas Cursor (Jesper Landberg - NXqjpo)
 * Enhanced with 120fps Physics, GSAP Blooming & Ultra-Smooth UI Kinematics
 *
 * Smooth UI Capabilities:
 * - Hidden on fresh load / reload (zero ghost circle at center)
 * - Organic GSAP blooming reveal (scale 0 -> 1) on first user interaction directly under pointer
 * - Butter-smooth framerate-independent exponential decay dampening (14.0 decay constant)
 * - Anti-aliased high-DPI Retina rendering with sub-pixel jitter elimination
 * - Fluid hover expansion (radius 10 -> 30) with cubic power3.out deceleration
 * - Tactile physical squish on mousedown / mouseup
 * - Seamless exit/re-entry blooming on window mouseleave/mouseenter
 * - Scroll-aware hover detection via rAF throttled elementFromPoint
 * - Automatic high-contrast inversion via mix-blend-mode: difference
 */

(function () {
  'use strict';

  function setupCursor() {
    let canvas = document.getElementById('cursor-canvas');
    if (!canvas) {
      canvas = document.createElement('canvas');
      canvas.id = 'cursor-canvas';
      canvas.className = 'reggae-cursor-canvas js-canvas';
      document.body.appendChild(canvas);
    }

    const ctx = canvas.getContext('2d', { alpha: true });
    let dpr = window.devicePixelRatio || 1;
    let width = window.innerWidth;
    let height = window.innerHeight;

    function resize() {
      dpr = window.devicePixelRatio || 1;
      width = window.innerWidth;
      height = window.innerHeight;
      canvas.width = Math.floor(width * dpr);
      canvas.height = Math.floor(height * dpr);
      canvas.style.width = width + 'px';
      canvas.style.height = height + 'px';
    }

    resize();
    window.addEventListener('resize', resize, { passive: true });

    // Initial state: off-screen and scale 0 until first user interaction
    let mouseX = -200;
    let mouseY = -200;
    let isVisible = false;
    let isHovering = false;
    let lastTime = performance.now();

    const circle = {
      x: -200,
      y: -200,
      radius: 10,
      baseRadius: 10,
      hoverRadius: 30,
      scale: 0
    };

    function onFirstPointer(x, y) {
      if (!isVisible) {
        isVisible = true;
        circle.x = x;
        circle.y = y;
        circle.scale = 0;
        document.documentElement.classList.add('has-custom-cursor');
        if (window.gsap) {
          gsap.to(circle, {
            scale: 1,
            duration: 0.36,
            ease: 'power3.out',
            overwrite: 'auto'
          });
        } else {
          circle.scale = 1;
        }
      }
    }

    function onPointerMove(x, y) {
      mouseX = x;
      mouseY = y;
      if (!isVisible) {
        onFirstPointer(x, y);
      }
    }

    window.addEventListener('mousemove', function (e) {
      onPointerMove(e.clientX, e.clientY);
    }, { passive: true });

    window.addEventListener('pointermove', function (e) {
      onPointerMove(e.clientX, e.clientY);
    }, { passive: true });

    window.addEventListener('touchmove', function (e) {
      if (e.touches && e.touches[0]) {
        onPointerMove(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchstart', function (e) {
      if (e.touches && e.touches[0]) {
        onPointerMove(e.touches[0].clientX, e.touches[0].clientY);
      }
    }, { passive: true });

    window.addEventListener('touchend', function () {
      if (window.gsap && isVisible) {
        gsap.to(circle, { scale: 0, duration: 0.28, ease: 'power2.inOut', overwrite: 'auto' });
      }
    }, { passive: true });

    // Smooth exit & re-entry when mouse leaves / re-enters browser viewport
    document.addEventListener('mouseleave', function () {
      if (window.gsap && isVisible) {
        gsap.to(circle, { scale: 0, duration: 0.24, ease: 'power2.in', overwrite: 'auto' });
      }
    });

    document.addEventListener('mouseenter', function (e) {
      if (e.clientX !== undefined && e.clientY !== undefined) {
        mouseX = e.clientX;
        mouseY = e.clientY;
        if (isVisible) {
          circle.x = mouseX;
          circle.y = mouseY;
          if (window.gsap) {
            gsap.to(circle, { scale: 1, duration: 0.32, ease: 'power3.out', overwrite: 'auto' });
          } else {
            circle.scale = 1;
          }
        }
      }
    });

    // Tactile physical squish on click
    window.addEventListener('mousedown', function () {
      if (!isVisible) return;
      if (window.gsap) {
        gsap.to(circle, { scale: 0.74, duration: 0.14, ease: 'power2.out', overwrite: 'auto' });
      } else {
        circle.scale = 0.74;
      }
    });

    window.addEventListener('mouseup', function () {
      if (!isVisible) return;
      if (window.gsap) {
        gsap.to(circle, { scale: 1, duration: 0.34, ease: 'power3.out', overwrite: 'auto' });
      } else {
        circle.scale = 1;
      }
    });

    // Interactive element hover selectors
    const interactiveSelector = [
      'a', 'button', '[role="button"]', 'input', 'textarea', 'select', 'label',
      '.btn-circle', '.btn-circle_link', '[hover-nav-item]', '[data-hover]',
      '.nav-item', '.tab_link', '.accordion-item', '.cursor-hover',
      '[data-modal-cta-btn]', '[data-modal-menu-btn]', '[data-tab-trigger]',
      '[data-filter-trigger]', '.card_preview', '.swiper-button-prev',
      '.swiper-button-next', '.lightbox-link', '.menu_btn', '.brand',
      '.footer_link', '[data-scroll-reveal]', '.loc-path-s_title',
      '[data-cookies="accept"]', '[data-cookies="decline"]',
      '.btn-menu', '.apart-card_link'
    ].join(', ');

    function setHover(hover) {
      if (isHovering === hover) return;
      isHovering = hover;
      if (window.gsap) {
        gsap.to(circle, {
          radius: hover ? circle.hoverRadius : circle.baseRadius,
          duration: hover ? 0.36 : 0.28,
          ease: 'power3.out',
          overwrite: 'auto'
        });
      } else {
        circle.radius = hover ? circle.hoverRadius : circle.baseRadius;
      }
    }

    document.addEventListener('mouseover', function (e) {
      const target = e.target && e.target.closest ? e.target.closest(interactiveSelector) : null;
      if (target) {
        setHover(true);
      }
    }, { passive: true });

    document.addEventListener('mouseout', function (e) {
      const target = e.target && e.target.closest ? e.target.closest(interactiveSelector) : null;
      if (target) {
        const related = e.relatedTarget && e.relatedTarget.closest ? e.relatedTarget.closest(interactiveSelector) : null;
        if (!related) {
          setHover(false);
        }
      }
    }, { passive: true });

    // Scroll-aware hover detection (throttled via rAF)
    let scrollCheckScheduled = false;
    window.addEventListener('scroll', function () {
      if (!isVisible || scrollCheckScheduled) return;
      scrollCheckScheduled = true;
      requestAnimationFrame(function () {
        scrollCheckScheduled = false;
        if (mouseX > 0 && mouseY > 0 && mouseX < width && mouseY < height) {
          const el = document.elementFromPoint(mouseX, mouseY);
          const target = el && el.closest ? el.closest(interactiveSelector) : null;
          setHover(Boolean(target));
        }
      });
    }, { passive: true });

    // High-refresh continuous render loop with framerate-independent exponential dampening
    function render(now) {
      if (!isVisible) {
        lastTime = now;
        requestAnimationFrame(render);
        return;
      }
      const dt = Math.min((now - lastTime) / 1000, 0.1);
      lastTime = now;

      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      ctx.clearRect(0, 0, width, height);
        // Silky exponential decay dampening
        // 14.0 factor creates the signature fluid Awwwards trailing glide without micro-jitters
        const factor = 1 - Math.exp(-14.0 * dt);
        
        const dx = mouseX - circle.x;
        const dy = mouseY - circle.y;

        // Sub-pixel snapping when resting to eliminate antialiasing shimmer
        if (Math.abs(dx) < 0.04 && Math.abs(dy) < 0.04) {
          circle.x = mouseX;
          circle.y = mouseY;
        } else {
          circle.x += dx * factor;
          circle.y += dy * factor;
        }

        const curRadius = circle.radius * circle.scale;
        if (curRadius > 0.2) {
          ctx.beginPath();
          ctx.arc(circle.x, circle.y, curRadius, 0, Math.PI * 2, false);
          ctx.fillStyle = '#ffffff';
          ctx.fill();
          ctx.closePath();
        }

      requestAnimationFrame(render);
    }

    requestAnimationFrame(render);
    window.__reggaeCursor = { circle, render, isVisible: () => isVisible, setHover };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupCursor);
  } else {
    setupCursor();
  }
})();
