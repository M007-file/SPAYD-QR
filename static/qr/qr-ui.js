console.log("qr-ui.js loaded");

const checkbox = document.getElementById("useGradient");
const block = document.getElementById("gradient-options");

console.log("checkbox:", checkbox);
console.log("block:", block);

if (checkbox && block) {
    const update = () => {
        console.log("update()", checkbox.checked);
        block.style.display = checkbox.checked ? "block" : "none";
    };

    checkbox.addEventListener("change", update);
    update();
}

document.addEventListener("DOMContentLoaded", () => {
    const blobs = document.querySelectorAll(".background span");
    if (!blobs.length) return;

    const state = [];
    let mouseX = 0;
    let mouseY = 0;

    // sledování myši (normalizované -0.5 .. +0.5)
    window.addEventListener("mousemove", e => {
        mouseX = (e.clientX / window.innerWidth) - 0.5;
        mouseY = (e.clientY / window.innerHeight) - 0.5;
        console.log("mouse", mouseX.toFixed(2), mouseY.toFixed(2));
    });

    blobs.forEach(el => {
        state.push({
            el,
            x: Math.random() * window.innerWidth,
            y: Math.random() * window.innerHeight,
            vx: (Math.random() - 0.5) * 0.3,
            vy: (Math.random() - 0.5) * 0.3,
            drift: 0.0015 + Math.random() * 0.003,
            depth: 0.2 + Math.random() * 0.8 // parallax hloubka
        });
    });

    const margin = 400;

    function animate() {
        state.forEach(p => {

            // Brownian motion
            p.vx += (Math.random() - 0.5) * p.drift;
            p.vy += (Math.random() - 0.5) * p.drift;

            // reakce na myš (parallax, jemná)
            p.vx += mouseX * 0.15 * p.depth;
            p.vy += mouseY * 0.15 * p.depth;

            // damping
            p.vx *= 0.992;
            p.vy *= 0.992;

            // clamp
            p.vx = Math.max(-0.4, Math.min(0.4, p.vx));
            p.vy = Math.max(-0.4, Math.min(0.4, p.vy));

            p.x += p.vx;
            p.y += p.vy;

            // wrap-around
            if (p.x < -margin) p.x = window.innerWidth + margin;
            if (p.y < -margin) p.y = window.innerHeight + margin;
            if (p.x > window.innerWidth + margin) p.x = -margin;
            if (p.y > window.innerHeight + margin) p.y = -margin;

            const r = (p.x + p.y) * 0.0015;

            p.el.style.transform =
                `translate3d(${p.x}px, ${p.y}px, 0) rotate(${r}deg)`;
        });

        requestAnimationFrame(animate);
    }

    animate();
});

document.addEventListener("DOMContentLoaded", () => {
    const btn = document.querySelector(".swap-colors");
    const c1 = document.getElementById("gradientColor1");
    const c2 = document.getElementById("gradientColor2");
    if (!btn || !c1 || !c2) return;

    btn.addEventListener("click", () => {
        const tmp = c1.value;
        c1.value = c2.value;
        c2.value = tmp;
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
