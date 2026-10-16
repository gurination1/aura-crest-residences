/**
 * Cleanroom Vendor Shim
 * Safe, zero-leak event & lifecycle hooks for page transitions.
 * Fully neutralizes external Webflow APIs, form beacons, and CDN trackers.
 */
window.Webflow = window.Webflow || [];
window.Webflow.push = function(fn) {
  if (typeof fn === 'function') {
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', fn);
    } else {
      fn();
    }
  }
};
window.Webflow.ready = function() {};
window.Webflow.destroy = function() {};
window.Webflow.require = function() { return {}; };
