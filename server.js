const http = require('http');
const fs = require('fs');
const path = require('path');

const PORT = 8080;
const PUBLIC_DIR = __dirname;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.svg': 'image/svg+xml',
  '.woff': 'font/woff',
  '.woff2': 'font/woff2',
  '.ttf': 'font/ttf',
  '.mp4': 'video/mp4',
  '.webm': 'video/webm',
  '.ico': 'image/x-icon',
};

const STATIC_EXTENSIONS = new Set([
  '.webm',
  '.mp4',
  '.png',
  '.jpg',
  '.jpeg',
  '.webp',
  '.avif',
  '.woff',
  '.woff2',
  '.ttf',
  '.svg',
  '.css',
  '.js',
  '.ico',
  '.json',
]);

const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host}`);
  let pathname = decodeURIComponent(parsedUrl.pathname);

  if (pathname === '/') {
    pathname = '/index.html';
  } else if (pathname === '/privacy' || pathname === '/privacy.html') {
    pathname = '/privacy.html';
  } else if (pathname === '/terms' || pathname === '/terms.html') {
    pathname = '/terms.html';
  } else if (!path.extname(pathname)) {
    pathname = pathname + '.html';
  }

  const filePath = path.join(PUBLIC_DIR, pathname);

  // Security check: ensure within PUBLIC_DIR
  if (!filePath.startsWith(PUBLIC_DIR)) {
    res.writeHead(403);
    return res.end('Forbidden');
  }

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain' });
      return res.end('Not Found: ' + pathname);
    }

    const ext = path.extname(filePath).toLowerCase();
    const contentType = MIME_TYPES[ext] || 'application/octet-stream';

    // Handle range request for video streaming
    if ((ext === '.mp4' || ext === '.webm') && req.headers.range && stats.size > 0) {
      const range = req.headers.range;
      const parts = range.replace(/bytes=/, '').split('-');
      const start = parseInt(parts[0], 10) || 0;
      const end = parts[1] ? Math.min(parseInt(parts[1], 10), stats.size - 1) : stats.size - 1;
      if (start > end || start >= stats.size) {
        res.writeHead(416, { 'Content-Range': `bytes */${stats.size}` });
        res.end();
        return;
      }
      const chunksize = end - start + 1;

      res.writeHead(206, {
        'Content-Range': `bytes ${start}-${end}/${stats.size}`,
        'Accept-Ranges': 'bytes',
        'Content-Length': chunksize,
        'Content-Type': contentType,
        'Cache-Control': 'no-cache',
        'Access-Control-Allow-Origin': '*',
      });

      const stream = fs.createReadStream(filePath, { start, end });
      stream.on('error', () => { res.end(); });
      stream.pipe(res);
      return;
    }

    const isHtml = ext === '.html' || !ext;
    const cacheControl = isHtml ? 'no-cache' : 'public, max-age=31536000, immutable';

    const headers = {
      'Content-Type': contentType,
      'Content-Length': stats.size,
      'Cache-Control': cacheControl,
      'Access-Control-Allow-Origin': '*',
    };

    if (ext === '.mp4' || ext === '.webm') {
      headers['Accept-Ranges'] = 'bytes';
    }

    res.writeHead(200, headers);

    const stream = fs.createReadStream(filePath);
    stream.pipe(res);
  });
});

const PORT_PRIMARY = 3001;
const PORT_SECONDARY = 8080;

server.listen(PORT_PRIMARY, '0.0.0.0', () => {
  console.log(`Aura Crest Residences Server running at http://localhost:${PORT_PRIMARY}/`);
});

const server2 = http.createServer(server.listeners('request')[0]);
server2.listen(PORT_SECONDARY, '0.0.0.0', () => {
  console.log(`Aura Crest Residences Mirror running at http://localhost:${PORT_SECONDARY}/`);
});
