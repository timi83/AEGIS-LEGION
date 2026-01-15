import React, { useEffect, useRef } from 'react';
import * as THREE from 'three';

export default function DottedSurface({ className, ...props }) {
    const containerRef = useRef(null);
    const sceneRef = useRef(null);
    const mouseX = useRef(0);
    const mouseY = useRef(0);

    useEffect(() => {
        if (!containerRef.current) return;

        const SEPARATION = 120;
        const AMOUNTX = 50;
        const AMOUNTY = 70;

        const scene = new THREE.Scene();

        const camera = new THREE.PerspectiveCamera(
            60,
            window.innerWidth / window.innerHeight,
            1,
            10000
        );
        camera.position.set(0, 500, 2200);

        const renderer = new THREE.WebGLRenderer({
            alpha: true,
            antialias: true,
        });
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000000, 0);

        containerRef.current.appendChild(renderer.domElement);

        const positions = [];
        const geometry = new THREE.BufferGeometry();

        // 5-color palette
        const palette = [
            new THREE.Color(0x00ff9d), // Green
            new THREE.Color(0x0055ff), // Blue
            new THREE.Color(0xffffff), // White
            new THREE.Color(0xff3333), // Red
            new THREE.Color(0xffff00), // Yellow
        ];

        for (let ix = 0; ix < AMOUNTX; ix++) {
            for (let iy = 0; iy < AMOUNTY; iy++) {
                const x = ix * SEPARATION - (AMOUNTX * SEPARATION) / 2;
                const z = iy * SEPARATION - (AMOUNTY * SEPARATION) / 2;
                positions.push(x, 0, z);
            }
        }

        geometry.setAttribute(
            'position',
            new THREE.Float32BufferAttribute(positions, 3)
        );

        const material = new THREE.PointsMaterial({
            size: 10,
            color: palette[0], // Start with first color
            vertexColors: false, // Unified color for all points
            transparent: true,
            opacity: 0.8,
            sizeAttenuation: true,
            blending: THREE.AdditiveBlending,
            depthWrite: false,
        });

        const points = new THREE.Points(geometry, material);
        scene.add(points);

        let count = 0;
        let animationId;

        const animate = () => {
            animationId = requestAnimationFrame(animate);

            // 1. Color Cycling
            const timeParams = count * 0.05;
            const colorIndex = Math.floor(timeParams) % palette.length;
            const nextColorIndex = (colorIndex + 1) % palette.length;
            const alpha = timeParams % 1;
            material.color.copy(palette[colorIndex]).lerp(palette[nextColorIndex], alpha);

            // 2. Wave Motion
            const positions = geometry.attributes.position.array;
            let i = 0;
            for (let ix = 0; ix < AMOUNTX; ix++) {
                for (let iy = 0; iy < AMOUNTY; iy++) {
                    const index = i * 3;
                    positions[index + 1] =
                        Math.sin((ix + count) * 0.3) * 50 +
                        Math.sin((iy + count) * 0.5) * 50;
                    i++;
                }
            }
            geometry.attributes.position.needsUpdate = true;

            // 3. Mouse Parallax (Interactive Camera)
            // Target is a slight offset based on mouse position
            const targetX = (mouseX.current * 100);
            const targetY = (mouseY.current * 100) + 500; // Keep the +500 elevation

            // Smoothly lerp current camera position only 5% of the way to target per frame (smooths jitter)
            camera.position.x += (targetX - camera.position.x) * 0.05;
            camera.position.y += (targetY - camera.position.y) * 0.05;

            camera.lookAt(scene.position);

            renderer.render(scene, camera);
            count += 0.1;
        };

        const handleResize = () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        };

        const handleMouseMove = (event) => {
            // Normalize mouse position from -1 to 1
            mouseX.current = (event.clientX / window.innerWidth) * 2 - 1;
            mouseY.current = -(event.clientY / window.innerHeight) * 2 + 1;
        };

        window.addEventListener('resize', handleResize);
        window.addEventListener('mousemove', handleMouseMove);

        animate();

        sceneRef.current = {
            scene, camera, renderer, points,
            cleanup: () => {
                window.removeEventListener('resize', handleResize);
                window.removeEventListener('mousemove', handleMouseMove);
                cancelAnimationFrame(animationId);
                geometry.dispose();
                material.dispose();
                renderer.dispose();
                if (containerRef.current && renderer.domElement) {
                    try { containerRef.current.removeChild(renderer.domElement); } catch (e) { }
                }
            },
        };

        return () => {
            sceneRef.current?.cleanup();
        };
    }, []);

    return (
        <div
            ref={containerRef}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                pointerEvents: 'none',
                zIndex: -10,
                ...props.style
            }}
            className={className}
            {...props}
        />
    );
}
