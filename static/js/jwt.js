(function () {
  'use strict';

  var config = window.jwtToolConfig || {};
  var state = {
    token: '',
    header: null,
    payload: null,
    signature: '',
    warnings: [],
    verifyStatus: 'not-run',
    verifyChecklist: []
  };

  function qs(id) {
    return document.getElementById(id);
  }

  function esc(text) {
    return String(text == null ? '' : text);
  }

  function pretty(value) {
    try {
      return JSON.stringify(value, null, 2);
    } catch (e) {
      return String(value);
    }
  }

  function b64UrlDecode(input) {
    var normalized = input.replace(/-/g, '+').replace(/_/g, '/');
    var pad = normalized.length % 4;
    if (pad) {
      normalized += '='.repeat(4 - pad);
    }
    var binary = atob(normalized);
    var bytes = new Uint8Array(binary.length);
    for (var i = 0; i < binary.length; i += 1) {
      bytes[i] = binary.charCodeAt(i);
    }
    return new TextDecoder().decode(bytes);
  }

  function b64UrlEncode(input) {
    var bytes = new TextEncoder().encode(input);
    var binary = '';
    for (var i = 0; i < bytes.length; i += 1) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
  }

  async function hmacSign(alg, secret, message) {
    var map = {
      HS256: 'SHA-256',
      HS384: 'SHA-384',
      HS512: 'SHA-512'
    };
    var hash = map[alg];
    if (!hash) {
      throw new Error('Unsupported HMAC algorithm');
    }
    var key = await crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(secret),
      { name: 'HMAC', hash: hash },
      false,
      ['sign']
    );
    var signature = await crypto.subtle.sign('HMAC', key, new TextEncoder().encode(message));
    var bytes = new Uint8Array(signature);
    var binary = '';
    for (var i = 0; i < bytes.length; i += 1) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/g, '');
  }

  function unixToIso(value) {
    var intVal = Number(value);
    if (!Number.isFinite(intVal)) {
      return null;
    }
    try {
      return new Date(intVal * 1000).toISOString();
    } catch (e) {
      return null;
    }
  }

  function parseToken(token) {
    var result = {
      valid: false,
      header: null,
      payload: null,
      signature: '',
      parts: [],
      warnings: []
    };

    if (!token) {
      result.warnings.push('Token is empty.');
      return result;
    }

    var parts = token.split('.');
    result.parts = parts;

    if (parts.length !== 3) {
      result.warnings.push('Token must contain exactly 3 parts.');
      return result;
    }

    var headerRaw;
    var payloadRaw;
    try {
      headerRaw = b64UrlDecode(parts[0]);
    } catch (e) {
      result.warnings.push('Header cannot be base64url-decoded.');
      return result;
    }

    try {
      payloadRaw = b64UrlDecode(parts[1]);
    } catch (e) {
      result.warnings.push('Payload cannot be base64url-decoded.');
      return result;
    }

    try {
      result.header = JSON.parse(headerRaw);
    } catch (e) {
      result.warnings.push('Header JSON is invalid.');
    }

    try {
      result.payload = JSON.parse(payloadRaw);
    } catch (e) {
      result.warnings.push('Payload JSON is invalid.');
    }

    result.signature = parts[2] || '';

    if (result.header && !result.header.alg) {
      result.warnings.push('Header is missing alg.');
    }

    if (result.payload) {
      var now = Math.floor(Date.now() / 1000);
      if (result.payload.exp != null) {
        if (!Number.isFinite(Number(result.payload.exp))) {
          result.warnings.push('Claim exp is not a valid Unix timestamp.');
        } else if (Number(result.payload.exp) < now) {
          result.warnings.push('Token is expired (exp in the past).');
        }
      } else {
        result.warnings.push('Claim exp is missing.');
      }

      if (result.payload.nbf != null) {
        if (!Number.isFinite(Number(result.payload.nbf))) {
          result.warnings.push('Claim nbf is not a valid Unix timestamp.');
        } else if (Number(result.payload.nbf) > now) {
          result.warnings.push('Token is not valid yet (nbf in the future).');
        }
      }

      if (result.payload.iat != null && !Number.isFinite(Number(result.payload.iat))) {
        result.warnings.push('Claim iat is not a valid Unix timestamp.');
      }
    }

    result.valid = Boolean(result.header && result.payload && parts.length === 3);
    return result;
  }

  function enrichClaims(payload) {
    if (!payload || typeof payload !== 'object') {
      return payload;
    }
    var clone = JSON.parse(JSON.stringify(payload));
    ['exp', 'iat', 'nbf'].forEach(function (key) {
      if (clone[key] != null) {
        var iso = unixToIso(clone[key]);
        if (iso) {
          clone[key + '_iso'] = iso;
        }
      }
    });
    return clone;
  }

  function setAlert(element, level, text) {
    if (!element) {
      return;
    }
    element.className = 'alert alert-' + level;
    element.textContent = text;
  }

  function updateDecodeUI(parsed) {
    var headerEl = qs('jwt-header-json');
    var payloadEl = qs('jwt-payload-json');
    var signatureEl = qs('jwt-signature');
    var warningsEl = qs('jwt-decode-warnings');
    var alertEl = qs('jwt-decode-alert');

    headerEl.textContent = parsed.header ? pretty(parsed.header) : '-';
    payloadEl.textContent = parsed.payload ? pretty(enrichClaims(parsed.payload)) : '-';
    signatureEl.textContent = parsed.signature || '-';

    warningsEl.innerHTML = '';
    parsed.warnings.forEach(function (warning) {
      var li = document.createElement('li');
      li.textContent = warning;
      warningsEl.appendChild(li);
    });

    if (!parsed.warnings.length) {
      var ok = document.createElement('li');
      ok.textContent = 'No structural warnings detected.';
      warningsEl.appendChild(ok);
      setAlert(alertEl, 'success', 'Token decoded successfully. This does not prove signature validity.');
    } else {
      setAlert(alertEl, 'warning', 'Decoded with warnings. Review claims and header fields carefully.');
    }
  }

  function activePanel(panel) {
    document.querySelectorAll('.jwt-tab').forEach(function (btn) {
      var on = btn.getAttribute('data-tab') === panel;
      btn.classList.toggle('btn-primary', on);
      btn.classList.toggle('active', on);
      btn.setAttribute('aria-selected', on ? 'true' : 'false');
    });

    document.querySelectorAll('.jwt-panel').forEach(function (card) {
      card.classList.toggle('active', card.getAttribute('data-panel') === panel);
    });
  }

  async function runVerify() {
    var token = qs('jwt-verify-token').value.trim();
    var mode = qs('jwt-verify-mode').value;
    var secret = qs('jwt-verify-secret').value;
    var checklist = [];

    function add(key, state, detail) {
      checklist.push({ key: key, state: state, detail: detail });
    }

    var parsed = parseToken(token);
    state.token = token;
    state.header = parsed.header;
    state.payload = parsed.payload;
    state.signature = parsed.signature;
    state.warnings = parsed.warnings;

    add('structure', parsed.parts.length === 3 ? 'ok' : 'fail', parsed.parts.length === 3 ? '3 parts' : 'Malformed token parts');

    if (!parsed.valid) {
      add('signature', 'fail', 'Token is malformed and cannot be verified');
      state.verifyStatus = 'malformed-token';
      state.verifyChecklist = checklist;
      renderVerifyChecklist();
      setAlert(qs('jwt-verify-alert'), 'error', 'Malformed token.');
      return;
    }

    var alg = mode === 'auto' ? (parsed.header.alg || '') : mode;
    add('header-review', parsed.header.kid || parsed.header.jku || parsed.header.jwk ? 'warn' : 'ok', 'Header fields reviewed');

    var now = Math.floor(Date.now() / 1000);
    var expOk = parsed.payload.exp == null || Number(parsed.payload.exp) >= now;
    var nbfOk = parsed.payload.nbf == null || Number(parsed.payload.nbf) <= now;
    var iatOk = parsed.payload.iat == null || Number.isFinite(Number(parsed.payload.iat));
    add('expiration', expOk ? 'ok' : 'fail', expOk ? 'exp check passed' : 'Token expired');
    add('not-before', nbfOk ? 'ok' : 'fail', nbfOk ? 'nbf check passed' : 'Token not active yet');
    add('issued-at', iatOk ? 'ok' : 'warn', iatOk ? 'iat looks sane' : 'iat looks invalid');

    if (alg === 'none') {
      state.verifyStatus = parsed.signature ? 'invalid-signature' : 'valid-signature';
      add('signature', parsed.signature ? 'fail' : 'ok', parsed.signature ? 'alg=none but signature is present' : 'No signature as expected for alg=none');
    } else if (['HS256', 'HS384', 'HS512'].indexOf(alg) !== -1) {
      if (!secret) {
        state.verifyStatus = 'missing-verification-material';
        add('signature', 'fail', 'Missing secret for HMAC verification');
      } else {
        var signedData = parsed.parts[0] + '.' + parsed.parts[1];
        var expected = await hmacSign(alg, secret, signedData);
        var ok = expected === parsed.signature;
        state.verifyStatus = ok ? 'valid-signature' : 'invalid-signature';
        add('signature', ok ? 'ok' : 'fail', ok ? 'HMAC signature is valid' : 'HMAC signature mismatch');
      }
    } else {
      state.verifyStatus = 'unsupported-algorithm';
      add('signature', 'fail', 'Unsupported algorithm: ' + alg);
    }

    state.verifyChecklist = checklist;
    renderVerifyChecklist();

    var level = state.verifyStatus === 'valid-signature' ? 'success' : 'warning';
    setAlert(qs('jwt-verify-alert'), level, 'Verification result: ' + state.verifyStatus + '.');
  }

  function renderVerifyChecklist() {
    var list = qs('jwt-verify-checklist');
    list.innerHTML = '';

    state.verifyChecklist.forEach(function (item) {
      var li = document.createElement('li');
      li.className = 'jwt-check jwt-check-' + item.state;
      li.textContent = item.key + ': ' + item.detail;
      list.appendChild(li);
    });
  }

  async function saveHistory(action, alertElementId) {
    if (!config.logUrl || !config.csrfToken) {
      return;
    }

    var inputData = {
      alg: state.header && state.header.alg ? state.header.alg : '-',
      token_parts: state.token ? state.token.split('.').length : 0,
      warnings: state.warnings.length,
      signature_status: state.verifyStatus
    };

    var summary = 'JWT ' + action + ' review. status=' + state.verifyStatus + ', warnings=' + state.warnings.length;

    try {
      var response = await fetch(config.logUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': config.csrfToken
        },
        body: JSON.stringify({
          action: action,
          input_data: inputData,
          generated_output: summary
        })
      });

      if (!response.ok) {
        throw new Error('Request failed');
      }

      if (alertElementId) {
        setAlert(qs(alertElementId), 'success', 'Saved to history automatically.');
      }
    } catch (error) {
      if (alertElementId) {
        setAlert(qs(alertElementId), 'error', 'Could not save history entry.');
      }
    }
  }

  function loadEncodeExample() {
    var now = Math.floor(Date.now() / 1000);
    qs('jwt-encode-header').value = pretty({ alg: 'HS256', typ: 'JWT' });
    qs('jwt-encode-payload').value = pretty({
      iss: 'shelltoolkit-lab',
      sub: 'student',
      aud: 'jwt-tool',
      iat: now,
      nbf: now,
      exp: now + 3600,
      scope: 'read:lab'
    });
    qs('jwt-encode-alg').value = 'HS256';
    qs('jwt-encode-secret').value = 'lab-secret';
  }

  function setupTabs() {
    document.querySelectorAll('.jwt-tab').forEach(function (btn) {
      btn.addEventListener('click', function () {
        activePanel(btn.getAttribute('data-tab'));
      });
    });
  }

  function setupDecode() {
    qs('jwt-decode-btn').addEventListener('click', function () {
      var token = qs('jwt-decode-token').value.trim();
      var parsed = parseToken(token);
      state.token = token;
      state.header = parsed.header;
      state.payload = parsed.payload;
      state.signature = parsed.signature;
      state.warnings = parsed.warnings;
      updateDecodeUI(parsed);
      saveHistory('decode', 'jwt-decode-alert');
    });

    qs('jwt-decode-example').addEventListener('click', function () {
      loadEncodeExample();
      qs('jwt-generate-btn').click();
      activePanel('decode');
    });

    qs('jwt-decode-clear').addEventListener('click', function () {
      qs('jwt-decode-token').value = '';
      state.token = '';
      state.header = null;
      state.payload = null;
      state.signature = '';
      state.warnings = [];
      updateDecodeUI({ header: null, payload: null, signature: '', warnings: [] });
    });

  }

  function setupEncode() {
    loadEncodeExample();

    qs('jwt-generate-btn').addEventListener('click', async function () {
      var header;
      var payload;
      try {
        header = JSON.parse(qs('jwt-encode-header').value);
        payload = JSON.parse(qs('jwt-encode-payload').value);
      } catch (e) {
        setAlert(qs('jwt-encode-alert'), 'error', 'Header/Payload must be valid JSON.');
        return;
      }

      var alg = qs('jwt-encode-alg').value;
      header.alg = alg;
      if (!header.typ) {
        header.typ = 'JWT';
      }

      var encodedHeader = b64UrlEncode(JSON.stringify(header));
      var encodedPayload = b64UrlEncode(JSON.stringify(payload));
      var signingInput = encodedHeader + '.' + encodedPayload;
      var signature = '';

      if (alg === 'none') {
        signature = '';
      } else {
        var secret = qs('jwt-encode-secret').value;
        if (!secret) {
          setAlert(qs('jwt-encode-alert'), 'error', 'Secret is required for HMAC algorithms.');
          return;
        }
        try {
          signature = await hmacSign(alg, secret, signingInput);
        } catch (e) {
          setAlert(qs('jwt-encode-alert'), 'error', 'Unable to sign token with selected algorithm.');
          return;
        }
      }

      var token = signingInput + '.' + signature;
      qs('jwt-encode-output').textContent = token;
      qs('jwt-decode-token').value = token;
      qs('jwt-verify-token').value = token;
      state.token = token;
      state.header = header;
      state.payload = payload;
      state.signature = signature;
      state.warnings = [];
      setAlert(qs('jwt-encode-alert'), 'success', 'Token generated locally in your browser.');
      saveHistory('encode', 'jwt-encode-alert');
    });

    qs('jwt-copy-generated').addEventListener('click', function () {
      var token = qs('jwt-encode-output').textContent.trim();
      if (!token || token === '-') {
        return;
      }
      navigator.clipboard.writeText(token);
    });

    qs('jwt-encode-example').addEventListener('click', loadEncodeExample);

    qs('jwt-encode-clear').addEventListener('click', function () {
      qs('jwt-encode-header').value = '';
      qs('jwt-encode-payload').value = '';
      qs('jwt-encode-secret').value = '';
      qs('jwt-encode-output').textContent = '-';
    });

    qs('jwt-send-decode').addEventListener('click', function () {
      activePanel('decode');
      qs('jwt-decode-btn').click();
    });

    qs('jwt-send-verify').addEventListener('click', function () {
      activePanel('verify');
      qs('jwt-verify-btn').click();
    });

  }

  function setupVerify() {
    qs('jwt-verify-btn').addEventListener('click', function () {
      runVerify().then(function () {
        saveHistory('verify', 'jwt-verify-alert');
      });
    });

    qs('jwt-verify-clear').addEventListener('click', function () {
      qs('jwt-verify-token').value = '';
      qs('jwt-verify-secret').value = '';
      state.verifyChecklist = [];
      renderVerifyChecklist();
    });

  }


  if (!qs('jwt-decode-btn')) {
    return;
  }

  setupTabs();
  setupDecode();
  setupEncode();
  setupVerify();
})();

