import { useEffect, useRef } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';

export default function CouchVisualization() {
    const mountRef = useRef<HTMLDivElement>(null);
    const frameId = useRef<number>(0);
    const sceneRef = useRef<THREE.Scene | null>(null);
    const rendererRef = useRef<THREE.WebGLRenderer | null>(null);
    const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
    const modelRef = useRef<THREE.Object3D | null>(null);

    useEffect(() => {
        if (!mountRef.current) return;

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = null; // Transparent background
        sceneRef.current = scene;

        // Camera setup
        const camera = new THREE.PerspectiveCamera(
            50, // Reduced FOV for less distortion
            mountRef.current.clientWidth / mountRef.current.clientHeight,
            0.1,
            1000
        );
        camera.position.set(3, 3, 8); // Pulled back further and higher
        camera.lookAt(0, 0, 0);
        cameraRef.current = camera;

        // Renderer setup
        const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        renderer.setSize(mountRef.current.clientWidth, mountRef.current.clientHeight);
        renderer.setPixelRatio(window.devicePixelRatio);
        renderer.setClearColor(0x000000, 0); // Transparent background
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        renderer.outputColorSpace = THREE.SRGBColorSpace;
        rendererRef.current = renderer;

        mountRef.current.appendChild(renderer.domElement);

        // Lighting setup
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        directionalLight.shadow.mapSize.width = 2048;
        directionalLight.shadow.mapSize.height = 2048;
        scene.add(directionalLight);

        const pointLight = new THREE.PointLight(0xffffff, 0.3);
        pointLight.position.set(-10, 10, -10);
        scene.add(pointLight);

        // Load the couch model using direct URL
        const loader = new GLTFLoader();
        console.log('Loading model from /couch.glb');
        
        loader.load(
            '/couch.glb',
            (gltf) => {
                console.log('Model loaded successfully!');
                const model = gltf.scene;
                
                // Log model info
                console.log('Model info:', {
                    children: model.children.length,
                    type: model.type,
                    userData: model.userData
                });
                
                model.traverse((child) => {
                    console.log('Child:', child.type, child.name);
                    if (child instanceof THREE.Mesh) {
                        child.castShadow = true;
                        child.receiveShadow = true;
                        // Ensure materials are visible
                        if (child.material) {
                            child.material.needsUpdate = true;
                        }
                    }
                });
                
                // Calculate bounding box to properly scale and center the model
                const box = new THREE.Box3().setFromObject(model);
                const size = box.getSize(new THREE.Vector3());
                const center = box.getCenter(new THREE.Vector3());
                
                console.log('Model dimensions:', { size, center });
                
                // Scale the model to fit nicely in view
                const maxDim = Math.max(size.x, size.y, size.z);
                const scale = maxDim > 0 ? 2 / maxDim : 1;
                model.scale.setScalar(scale);
                
                // Center the model
                model.position.copy(center).multiplyScalar(-scale);
                model.position.y -= (size.y * scale) / 2;
                
                scene.add(model);
                modelRef.current = model;
            },
            (progress) => {
                console.log('Loading progress:', (progress.loaded / progress.total) * 100 + '%');
            },
            (error) => {
                console.error('Failed to load model:', error);
                // Add a fallback cube for debugging
                const geometry = new THREE.BoxGeometry(1, 1, 1);
                const material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
                const cube = new THREE.Mesh(geometry, material);
                scene.add(cube);
                modelRef.current = cube;
                console.log('Added fallback cube');
            }
        );

        // Animation loop
        const animate = () => {
            frameId.current = requestAnimationFrame(animate);
            
            // Rotate the model slowly
            if (modelRef.current) {
                modelRef.current.rotation.y += 0.005;
            }
            
            renderer.render(scene, camera);
        };
        animate();

        // Handle resize
        const handleResize = () => {
            if (!mountRef.current || !camera || !renderer) return;
            
            const width = mountRef.current.clientWidth;
            const height = mountRef.current.clientHeight;
            
            camera.aspect = width / height;
            camera.updateProjectionMatrix();
            renderer.setSize(width, height);
        };

        window.addEventListener('resize', handleResize);

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);
            
            if (frameId.current) {
                cancelAnimationFrame(frameId.current);
            }
            
            if (mountRef.current && rendererRef.current) {
                mountRef.current.removeChild(rendererRef.current.domElement);
            }
            
            if (rendererRef.current) {
                rendererRef.current.dispose();
            }
            
            if (sceneRef.current) {
                sceneRef.current.clear();
            }
        };
    }, []);

    return (
        <div 
            ref={mountRef} 
            className="w-full h-full rounded-lg overflow-hidden"
            style={{ minHeight: '200px' }}
        />
    );
}