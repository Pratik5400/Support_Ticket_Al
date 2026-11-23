"""
cursor_bg.py - Google Antigravity Cursor-Following Background Animation for Streamlit.
Injects a high-performance interactive canvas into the parent Streamlit DOM.
"""

import streamlit as st
import streamlit.components.v1 as components


def inject_cursor_background():
    """
    Injects the Google Antigravity interactive dot-grid canvas and cursor-following
    radial glow into the Streamlit parent document.
    """
    # Transparent container CSS so the canvas renders behind Streamlit widgets
    st.markdown("""
    <style>
    [data-testid="stApp"],
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"] {
        background: transparent !important;
    }
    [data-testid="stAppViewContainer"] > .main {
        position: relative;
        z-index: 1;
    }
    </style>
    """, unsafe_allow_html=True)

    # JavaScript payload executed in the parent DOM via an invisible iframe component
    js_code = """
    <script>
    (function() {
        try {
            const parentDoc = window.parent.document;
            const parentWin = window.parent;
            if (!parentDoc || !parentWin) return;

            // Check if user prefers reduced motion
            const prefersReducedMotion = parentWin.matchMedia('(prefers-reduced-motion: reduce)').matches;
            if (prefersReducedMotion) return;

            // Clean up existing instance if already present on re-render
            if (parentWin.__agCleanUp) {
                parentWin.__agCleanUp();
            }

            // Create canvas if not already in parent document
            let canvas = parentDoc.getElementById('ag-bg');
            if (!canvas) {
                canvas = parentDoc.createElement('canvas');
                canvas.id = 'ag-bg';
                canvas.style.position = 'fixed';
                canvas.style.top = '0';
                canvas.style.left = '0';
                canvas.style.width = '100vw';
                canvas.style.height = '100vh';
                canvas.style.zIndex = '0';
                canvas.style.pointerEvents = 'none';
                parentDoc.body.prepend(canvas);
            }

            const ctx = canvas.getContext('2d');
            let width = 0;
            let height = 0;
            let dpr = parentWin.devicePixelRatio || 1;
            let dots = [];
            const SPACING = 20; // Distance between grid dots in pixels
            const INFLUENCE_RADIUS = 180; // Cursor interaction radius
            const BASE_RADIUS = 1.15; // Unhovered dot radius
            const BASE_COLOR = 'rgba(195, 206, 226, 0.40)'; // Subtle light gray-blue dot

            // Antigravity gradient color stops: Blue -> Violet -> Pink
            const COLOR_BLUE = [66, 133, 244];   // #4285F4
            const COLOR_VIOLET = [161, 66, 244]; // #A142F4
            const COLOR_PINK = [245, 56, 160];   // #F538A0

            function interpolateColor(colorA, colorB, t) {
                return [
                    Math.round(colorA[0] + (colorB[0] - colorA[0]) * t),
                    Math.round(colorA[1] + (colorB[1] - colorA[1]) * t),
                    Math.round(colorA[2] + (colorB[2] - colorA[2]) * t)
                ];
            }

            function getGradientColor(factor, angle) {
                // Map normalized angle (0 to 1) to three-stop gradient
                const normAngle = (Math.sin(angle) + 1) / 2;
                let rgb;
                if (normAngle < 0.5) {
                    rgb = interpolateColor(COLOR_BLUE, COLOR_VIOLET, normAngle * 2);
                } else {
                    rgb = interpolateColor(COLOR_VIOLET, COLOR_PINK, (normAngle - 0.5) * 2);
                }
                const alpha = Math.min(0.95, 0.40 + factor * 0.55);
                return `rgba(${rgb[0]}, ${rgb[1]}, ${rgb[2]}, ${alpha.toFixed(2)})`;
            }

            function initGrid() {
                dpr = parentWin.devicePixelRatio || 1;
                width = parentWin.innerWidth;
                height = parentWin.innerHeight;
                canvas.width = width * dpr;
                canvas.height = height * dpr;
                ctx.scale(dpr, dpr);

                dots = [];
                const cols = Math.ceil(width / SPACING) + 1;
                const rows = Math.ceil(height / SPACING) + 1;

                for (let r = 0; r <= rows; r++) {
                    for (let c = 0; c <= cols; c++) {
                        const ox = c * SPACING;
                        const oy = r * SPACING;
                        dots.push({
                            ox: ox,
                            oy: oy,
                            x: ox,
                            y: oy,
                            r: BASE_RADIUS,
                            targetR: BASE_RADIUS,
                            color: BASE_COLOR
                        });
                    }
                }
            }

            const mouse = {
                x: -9999,
                y: -9999,
                smoothX: -9999,
                smoothY: -9999,
                active: false
            };

            function onMouseMove(e) {
                mouse.x = e.clientX;
                mouse.y = e.clientY;
                if (!mouse.active) {
                    mouse.smoothX = e.clientX;
                    mouse.smoothY = e.clientY;
                    mouse.active = true;
                }
            }

            function onMouseLeave() {
                mouse.active = false;
            }

            function onResize() {
                initGrid();
            }

            parentWin.addEventListener('mousemove', onMouseMove, { passive: true });
            parentDoc.addEventListener('mouseleave', onMouseLeave, { passive: true });
            parentWin.addEventListener('resize', onResize, { passive: true });

            initGrid();

            let animId = null;

            function render() {
                if (!parentDoc.hidden) {
                    ctx.clearRect(0, 0, width, height);

                    // Smooth cursor tracking with lerp
                    if (mouse.active) {
                        mouse.smoothX += (mouse.x - mouse.smoothX) * 0.10;
                        mouse.smoothY += (mouse.y - mouse.smoothY) * 0.10;

                        // Soft radial ambient glow following cursor
                        const glowRadius = INFLUENCE_RADIUS * 1.15;
                        const glow = ctx.createRadialGradient(
                            mouse.smoothX, mouse.smoothY, 0,
                            mouse.smoothX, mouse.smoothY, glowRadius
                        );
                        glow.addColorStop(0, 'rgba(66, 133, 244, 0.14)');
                        glow.addColorStop(0.45, 'rgba(161, 66, 244, 0.07)');
                        glow.addColorStop(0.8, 'rgba(245, 56, 160, 0.02)');
                        glow.addColorStop(1, 'rgba(255, 255, 255, 0)');

                        ctx.fillStyle = glow;
                        ctx.beginPath();
                        ctx.arc(mouse.smoothX, mouse.smoothY, glowRadius, 0, Math.PI * 2);
                        ctx.fill();
                    }

                    // Update and draw grid dots
                    for (let i = 0; i < dots.length; i++) {
                        const dot = dots[i];
                        let targetX = dot.ox;
                        let targetY = dot.oy;
                        let targetR = BASE_RADIUS;
                        let targetColor = BASE_COLOR;

                        if (mouse.active) {
                            const dx = dot.ox - mouse.smoothX;
                            const dy = dot.oy - mouse.smoothY;
                            const dist = Math.sqrt(dx * dx + dy * dy);

                            if (dist < INFLUENCE_RADIUS) {
                                const factor = (1 - dist / INFLUENCE_RADIUS);
                                // Smooth bell curve repulsion
                                const push = Math.sin(factor * Math.PI * 0.5) * 26;
                                const angle = Math.atan2(dy, dx);

                                targetX = dot.ox + Math.cos(angle) * push;
                                targetY = dot.oy + Math.sin(angle) * push;
                                targetR = BASE_RADIUS + factor * 1.6;
                                targetColor = getGradientColor(factor, angle);
                            }
                        }

                        // Smooth interpolation (lerp)
                        dot.x += (targetX - dot.x) * 0.10;
                        dot.y += (targetY - dot.y) * 0.10;
                        dot.r += (targetR - dot.r) * 0.12;

                        ctx.fillStyle = targetColor;
                        ctx.beginPath();
                        ctx.arc(dot.x, dot.y, dot.r, 0, Math.PI * 2);
                        ctx.fill();
                    }
                }

                animId = parentWin.requestAnimationFrame(render);
            }

            animId = parentWin.requestAnimationFrame(render);

            // Store cleanup handle on parent window
            parentWin.__agCleanUp = function() {
                if (animId) {
                    parentWin.cancelAnimationFrame(animId);
                }
                parentWin.removeEventListener('mousemove', onMouseMove);
                parentDoc.removeEventListener('mouseleave', onMouseLeave);
                parentWin.removeEventListener('resize', onResize);
            };

        } catch (err) {
            console.warn('[SupportAI] Antigravity cursor background init:', err);
        }
    })();
    </script>
    """
    components.html(js_code, height=0, width=0)
