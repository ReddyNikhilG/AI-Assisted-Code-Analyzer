const http = require('http');
const https = require('https');
const url = require('url');

/**
 * Send code to the CodeSense AI backend for analysis.
 * Uses only Node.js built-in modules (no external dependencies).
 */
function analyzeCode(backendUrl, code) {
    return new Promise((resolve, reject) => {
        const parsed = url.parse(backendUrl + '/analyze');
        const payload = JSON.stringify({ code: code });
        const transport = parsed.protocol === 'https:' ? https : http;

        const options = {
            hostname: parsed.hostname,
            port: parsed.port,
            path: parsed.path,
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Content-Length': Buffer.byteLength(payload)
            },
            timeout: 15000
        };

        const req = transport.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        resolve(JSON.parse(body));
                    } catch (e) {
                        reject(new Error('Invalid JSON response from backend'));
                    }
                } else {
                    reject(new Error(`Backend returned status ${res.statusCode}: ${body}`));
                }
            });
        });

        req.on('error', (err) => {
            reject(new Error(`Cannot connect to CodeSense backend at ${backendUrl}: ${err.message}`));
        });

        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Backend request timed out after 15 seconds'));
        });

        req.write(payload);
        req.end();
    });
}

/**
 * Check if the backend is healthy.
 */
function checkHealth(backendUrl) {
    return new Promise((resolve, reject) => {
        const parsed = url.parse(backendUrl + '/health');
        const transport = parsed.protocol === 'https:' ? https : http;

        const req = transport.get(parsed, (res) => {
            let body = '';
            res.on('data', (chunk) => { body += chunk; });
            res.on('end', () => {
                if (res.statusCode === 200) {
                    try {
                        resolve(JSON.parse(body));
                    } catch (e) {
                        reject(new Error('Invalid health response'));
                    }
                } else {
                    reject(new Error(`Health check failed: ${res.statusCode}`));
                }
            });
        });

        req.on('error', (err) => {
            reject(new Error(`Backend unreachable: ${err.message}`));
        });

        req.on('timeout', () => {
            req.destroy();
            reject(new Error('Health check timed out'));
        });
    });
}

module.exports = { analyzeCode, checkHealth };
