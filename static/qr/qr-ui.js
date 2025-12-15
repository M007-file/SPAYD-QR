console.log("qr-ui.js loaded");

/* =========================================================
   GRADIENT TOGGLE
   ========================================================= */
const checkbox = document.getElementById("useGradient");
const block = document.getElementById("gradient-options");

if (checkbox && block) {
    const update = () => {
        block.style.display = checkbox.checked ? "block" : "none";
    };
    checkbox.addEventListener("change", update);
    update();
}

/* =========================================================
   LÁVOVÉ POZADÍ – BLOBS
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    const blobs = document.querySelectorAll(".background .blob");
    if (!blobs.length) return;

    const W = () => window.innerWidth;
    const H = () => window.innerHeight;

    const state = [];
    const COUNT = blobs.length;

    /* ---------- MYŠ ---------- */
    let mouseX = 0;
    let mouseY = 0;
    let mouseActive = false;

    window.addEventListener("mousemove", e => {
        mouseX = e.clientX;
        mouseY = e.clientY;
        mouseActive = true;
    });

    window.addEventListener("mouseleave", () => {
        mouseActive = false;
    });

    /* ---------- PARAMETRY ---------- */
    const NOISE_SCALE = 0.0008;
    const NOISE_TIME  = 0.00015;
    const MAX_SPEED   = 0.35;
    const DAMPING     = 0.985;
    const REPULSION_RADIUS = 160;
    const REPULSION_FORCE  = 0.45;
    const TURN_CHANCE = 0.002;

    let time = Math.random() * 1000;

    /* ---------- NOISE ---------- */
    function hash(x, y) {
        return Math.sin(x * 127.1 + y * 311.7) * 43758.5453 % 1;
    }

    function noise(x, y) {
        const xi = Math.floor(x);
        const yi = Math.floor(y);
        const xf = x - xi;
        const yf = y - yi;

        const n00 = hash(xi, yi);
        const n10 = hash(xi + 1, yi);
        const n01 = hash(xi, yi + 1);
        const n11 = hash(xi + 1, yi + 1);

        const u = xf * xf * (3 - 2 * xf);
        const v = yf * yf * (3 - 2 * yf);

        return (
            n00 * (1 - u) * (1 - v) +
            n10 * u * (1 - v) +
            n01 * (1 - u) * v +
            n11 * u * v
        );
    }

    function curl(x, y, t) {
        const e = 0.001;
        return {
            x: noise(x * NOISE_SCALE, (y + e + t) * NOISE_SCALE) -
               noise(x * NOISE_SCALE, (y - e + t) * NOISE_SCALE),
            y: noise((x - e) * NOISE_SCALE, (y + t) * NOISE_SCALE) -
               noise((x + e) * NOISE_SCALE, (y + t) * NOISE_SCALE)
        };
    }

    /* ---------- INIT ---------- */
    blobs.forEach(el => {
        state.push({
            el,
            x: Math.random() * W(),
            y: Math.random() * H(),
            vx: 0,
            vy: 0,
            mass: 0.6 + Math.random() * 1.4,
            intent: Math.random() * Math.PI * 2,

            scalePhase: Math.random() * Math.PI * 2,
            scaleSpeed: 0.004 + Math.random() * 0.01,
            scaleAmp: 0.08 + Math.random() * 0.15,

            hover: 0,
            clickBoost: 0
        });
    });

    const margin = 300;

    blobs.forEach((el, i) => {
        el.addEventListener("click", e => {
            e.stopPropagation();
            state[i].clickBoost = 1;
        });
    });

    /* ---------- ANIMACE ---------- */
    function animate() {
        time++;

        // odpuzování blobů
        for (let i = 0; i < COUNT; i++) {
            for (let j = i + 1; j < COUNT; j++) {
                const a = state[i];
                const b = state[j];

                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const d2 = dx * dx + dy * dy;

                if (d2 < REPULSION_RADIUS ** 2 && d2 > 0.01) {
                    const d = Math.sqrt(d2);
                    const f = (1 - d / REPULSION_RADIUS) * REPULSION_FORCE;

                    const fx = (dx / d) * f;
                    const fy = (dy / d) * f;

                    a.vx += fx / a.mass;
                    a.vy += fy / a.mass;
                    b.vx -= fx / b.mass;
                    b.vy -= fy / b.mass;
                }
            }
        }

        state.forEach(p => {
            // myš
            if (mouseActive) {
                const dx = mouseX - p.x;
                const dy = mouseY - p.y;
                const d2 = dx * dx + dy * dy;
                const radius = 220;

                if (d2 < radius * radius) {
                    const d = Math.sqrt(d2);
                    const force = (1 - d / radius) * 0.08;

                    p.vx += (dx / d) * force;
                    p.vy += (dy / d) * force;
                    p.hover = Math.min(1, p.hover + 0.05);
                } else {
                    p.hover *= 0.95;
                }
            } else {
                p.hover *= 0.95;
            }

            // lávový proud
            const c = curl(p.x, p.y, time * NOISE_TIME);
            p.vx += c.x * 0.6;
            p.vy += c.y * 0.6;

            if (Math.random() < TURN_CHANCE) {
                p.intent += (Math.random() - 0.5) * Math.PI;
            }

            p.vx += Math.cos(p.intent) * 0.02;
            p.vy += Math.sin(p.intent) * 0.02;

            p.vx *= DAMPING;
            p.vy *= DAMPING;

            const sp = Math.hypot(p.vx, p.vy);
            if (sp > MAX_SPEED) {
                p.vx *= MAX_SPEED / sp;
                p.vy *= MAX_SPEED / sp;
            }

            p.x += p.vx;
            p.y += p.vy;

            if (p.x < -margin) p.x = W() + margin;
            if (p.y < -margin) p.y = H() + margin;
            if (p.x > W() + margin) p.x = -margin;
            if (p.y > H() + margin) p.y = -margin;

            // vizuál
            const rot = Math.atan2(p.vy, p.vx) * 57.3;
            p.scalePhase += p.scaleSpeed;
            p.clickBoost *= 0.92;

            const scale =
                (1 +
                Math.sin(p.scalePhase) * p.scaleAmp) *
                (1 + p.hover * 0.25 + p.clickBoost * 0.4);

            p.el.style.transform =
                `translate3d(${p.x}px, ${p.y}px, 0)
                 rotate(${rot}deg)
                 scale(${scale})`;

            p.el.style.filter =
                `brightness(${1 + p.hover * 0.15 + p.clickBoost * 0.2})`;
        });

        requestAnimationFrame(animate);
    }

    animate();
});

/* =========================================================
   OSTATNÍ UI
   ========================================================= */
document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector(".swap-colors");
    const c1 = document.getElementById("gradientColor1");
    const c2 = document.getElementById("gradientColor2");
    if (!btn || !c1 || !c2) return;

    btn.addEventListener("click", () => {
        [c1.value, c2.value] = [c2.value, c1.value];
        c1.dispatchEvent(new Event("input", { bubbles: true }));
        c2.dispatchEvent(new Event("input", { bubbles: true }));
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const toggle = document.getElementById("qrConfigToggle");
    const content = document.getElementById("qrConfigContent");
    if (!toggle || !content) return;

    toggle.addEventListener("click", () => {
        toggle.classList.toggle("open");
        content.classList.toggle("open");
    });
});
