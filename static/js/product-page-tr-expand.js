const onlyOne = false; // if true, animations are broken on various browsers
const openRows = Object.create(null); // key -> true if open

document.addEventListener('DOMContentLoaded', () => {
    const table = document.getElementById('offers');
    if (!table) return;
    const tbody = table.tBodies[0] || table.querySelector('tbody')
;
    let currentKey = null,
        animating = false,
        pendingKey = null;
    const DUR = 240,
        SLACK = 120; // ms (matches CSS transition)

    const forceReflow = (el) => el.getBoundingClientRect().height; // patch insta-close on firefox
    const naturalH   = (el) => Math.ceil(el.scrollHeight);
    const currentH   = (el) => Math.ceil(el.getBoundingClientRect().height);


    const byKey = {};
    [...tbody.querySelectorAll('tr.data-row')].forEach((r, i) => {
        const key = r.dataset.key || String(i+1); r.dataset.key = key;
        const trD = r.nextElementSibling;
        if (!trD || !trD.classList.contains('details-row'))
            return;
        const wrap = trD.querySelector('.details');
        if (!wrap)
            return;
        wrap.style.height = '0px';
        byKey[key] = {row: r, details: trD, wrap };
    });

    tbody.addEventListener('click', e => {
        const row = e.target.closest('tr.data-row');
        row && act(row.dataset.key);
    });

    function act(k) {
        if (!onlyOne) {
            toggle(k);
            return;
        }
        if (animating) {
            pendingKey = k;  // remember the last click
            return;
        }

        if (openRows[k]) {
            animating = true;
            closeK(k, done);
            return;
        }
        if (currentKey == null) {
            animating = true;
            openK(k, done);
            return;
        }
        // switch current -> k
        animating = true;
        switchTo(k, done);

        function done() {
            animating = false;
            if (pendingKey != null) {
                const next = pendingKey;
                pendingKey = null;
                // run next tick to avoid re-entrancy
                setTimeout(() => act(next), 0);
            }
        }
    }

    function toggle(k) {
        openRows[k] ? closeK(k) : openK(k);
    }

    function openK(k, cb) {
        const w = byKey[k]?.wrap;
        if (!w)
            return cb && cb();
        byKey[k]?.row.classList.add('opening-started');
        const h = w.scrollHeight;
        w.style.height = '0px';
        forceReflow(w);
        requestAnimationFrame(() => {
            w.style.height = h+'px';
            onHeightEnd(w, () => {
                w.style.height = 'auto';
                openRows[k] = true;
                currentKey = k;
                byKey[k]?.row.classList.add('is-open');
                cb && cb();
            });
        });
    }

    function closeK(k, cb) {
        const w = byKey[k]?.wrap;
        if (!w)
            return cb && cb();
        w.style.height = w.scrollHeight + 'px';
        forceReflow(w);
        requestAnimationFrame(() => {
            w.style.height = '0px';
            onHeightEnd(w, () => {
                delete openRows[k];
                if (currentKey === k)
                    currentKey = null;
                byKey[k]?.row.classList.remove('is-open', 'opening-started');
                cb && cb();
            });
        });

    }

    function switchTo(k, cb) {
        const oldW = byKey[currentKey]?.wrap, newW = byKey[k]?.wrap;
        if (!oldW || !newW)
            return cb && cb();

        byKey[k]?.row.classList.add('opening-started');

        const hOld = oldW.scrollHeight, hNew = newW.scrollHeight;
        oldW.style.height = hOld+'px';
        newW.style.height = '0px';

        forceReflow(oldW);
        forceReflow(newW);

        let done = 0;
        const both = () => {
            if (++done === 2) {
                newW.style.height = 'auto';
                const prevKey = currentKey;
                delete openRows[prevKey];
                openRows[k] = true;
                currentKey = k;
                byKey[prevKey]?.row.classList.remove('is-open', 'opening-started');
                byKey[k]?.row.classList.add('is-open');
                cb && cb();
            }
        }
        requestAnimationFrame(() => {
            oldW.style.height = '0px';
            newW.style.height = hNew+'px';
            onHeightEnd(oldW, both);
            onHeightEnd(newW, both);
        });
    }

    // --- utilities ---
    function onHeightEnd(el, fn) {
        // robust end with token + timeout fallback
        const token = Math.random().toString(36).slice(2);
        el.dataset.tok = token;
        let fired = false;
        const handler = e => {
            if (e.propertyName !== 'height' || el.dataset.tok !== token || fired)
                return;
            fired = true;
            el.removeEventListener('transitionend', handler);
            fn();
        }
        el.addEventListener('transitionend', handler, { once: true });
        setTimeout(() => {
            if (fired)
                return;
            fired = true;
            el.removeEventListener('transitionend', handler);
            fn();
        }, DUR + SLACK);
    }
});