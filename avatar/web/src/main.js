import * as THREE from "three";
import { FayClient } from "./fay-client.js";
import "./style.css";

const canvas = document.querySelector("#scene");
const stateLabel = document.querySelector("#state");
const caption = document.querySelector("#caption");
const presence = document.querySelector("#presence");

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.1;

const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x070b12, 0.065);

const camera = new THREE.PerspectiveCamera(34, 1, 0.1, 100);
camera.position.set(0, 0.1, 7.4);

scene.add(new THREE.HemisphereLight(0xdcecff, 0x202533, 2.2));
const keyLight = new THREE.DirectionalLight(0xffe4cf, 4.2);
keyLight.position.set(3, 4, 5);
scene.add(keyLight);
const rimLight = new THREE.DirectionalLight(0x5ba6ff, 5.5);
rimLight.position.set(-4, 2, -3);
scene.add(rimLight);

// Temporary diagnostic avatar. This is replaced by the selected rigged GLB
// only after rendering, audio playback, and the Fay connection pass on Spark.
const avatar = new THREE.Group();
scene.add(avatar);

const skin = new THREE.MeshPhysicalMaterial({
  color: 0xb97864,
  roughness: 0.58,
  clearcoat: 0.12,
  clearcoatRoughness: 0.7,
});
const dark = new THREE.MeshStandardMaterial({ color: 0x111723, roughness: 0.5 });
const white = new THREE.MeshPhysicalMaterial({ color: 0xf6f7fb, roughness: 0.2 });

const shoulders = new THREE.Mesh(new THREE.CapsuleGeometry(1.25, 1.35, 8, 24), dark);
shoulders.scale.set(1.25, 0.82, 0.7);
shoulders.position.y = -1.8;
avatar.add(shoulders);

const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.42, 0.85, 32), skin);
neck.position.y = -0.78;
avatar.add(neck);

const head = new THREE.Mesh(new THREE.SphereGeometry(1.12, 64, 48), skin);
head.scale.set(0.88, 1.12, 0.92);
head.position.y = 0.45;
avatar.add(head);

const hair = new THREE.Mesh(
  new THREE.SphereGeometry(1.17, 48, 32, 0, Math.PI * 2, 0, Math.PI * 0.62),
  dark,
);
hair.scale.set(0.9, 1.12, 0.95);
hair.position.set(0, 0.56, -0.02);
avatar.add(hair);

for (const x of [-0.34, 0.34]) {
  const eye = new THREE.Mesh(new THREE.SphereGeometry(0.13, 24, 16), white);
  eye.scale.set(1.25, 0.65, 0.5);
  eye.position.set(x, 0.62, 0.91);
  avatar.add(eye);
  const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.055, 16, 12), dark);
  pupil.position.set(x, 0.62, 0.995);
  avatar.add(pupil);
}

const mouth = new THREE.Mesh(
  new THREE.CapsuleGeometry(0.075, 0.42, 6, 16),
  new THREE.MeshStandardMaterial({ color: 0x54262c, roughness: 0.8 }),
);
mouth.rotation.z = Math.PI / 2;
mouth.position.set(0, 0.04, 1.015);
mouth.scale.set(1, 0.25, 0.35);
avatar.add(mouth);

const floor = new THREE.Mesh(
  new THREE.CircleGeometry(8, 96),
  new THREE.MeshStandardMaterial({ color: 0x0b111c, roughness: 0.88 }),
);
floor.rotation.x = -Math.PI / 2;
floor.position.y = -2.53;
scene.add(floor);

let analyser = null;
let audioContext = null;
let audioElement = null;
let speakingEnergy = 0;
let currentObjectUrl = null;

async function playAvatarAudio(httpValue) {
  if (!httpValue) return;
  stateLabel.textContent = "Downloading speech…";

  const sourceUrl = new URL(httpValue);
  const proxyUrl = `/fay/audio/${encodeURIComponent(sourceUrl.pathname.split("/").pop())}`;
  const response = await fetch(proxyUrl);
  if (!response.ok) throw new Error(`Audio request failed: ${response.status}`);
  const blob = await response.blob();

  if (currentObjectUrl) URL.revokeObjectURL(currentObjectUrl);
  currentObjectUrl = URL.createObjectURL(blob);
  audioElement?.pause();
  audioElement = new Audio(currentObjectUrl);

  audioContext ??= new AudioContext();
  if (audioContext.state === "suspended") await audioContext.resume();
  const source = audioContext.createMediaElementSource(audioElement);
  analyser = audioContext.createAnalyser();
  analyser.fftSize = 256;
  source.connect(analyser);
  analyser.connect(audioContext.destination);

  audioElement.addEventListener("play", () => {
    stateLabel.textContent = "Speaking";
  });
  audioElement.addEventListener("ended", () => {
    stateLabel.textContent = "Listening";
    speakingEnergy = 0;
  });
  await audioElement.play();
}

async function resolveWebSocketUrl() {
  const configured = new URLSearchParams(location.search).get("ws");
  if (configured) return configured;
  const response = await fetch("/fay/config", { cache: "no-store" });
  if (!response.ok) throw new Error(`Configuration request failed: ${response.status}`);
  const config = await response.json();
  return config.wsUrl;
}

let client = null;

async function startFayClient() {
  const wsUrl = await resolveWebSocketUrl();
  client = new FayClient({ url: wsUrl, username: "User" });
  client.addEventListener("status", ({ detail }) => {
    const connected = detail.state === "connected";
    presence.classList.toggle("connected", connected);
    stateLabel.textContent = connected ? "Connected · Listening" : `Fay ${detail.state}`;
  });
  client.addEventListener("message", ({ detail: message }) => {
    if (message.Topic !== "human") return;
    const data = message.Data ?? {};
    if (data.Text || (data.Key === "text" && data.Value)) {
      caption.textContent = data.Text || data.Value;
    }
    if (data.Key === "log" && data.Value) stateLabel.textContent = data.Value;
    if (data.Key === "audio" && data.HttpValue) {
      playAvatarAudio(data.HttpValue).catch((error) => {
        stateLabel.textContent = `Audio error: ${error.message}`;
      });
    }
  });
  client.addEventListener("error", () => {
    stateLabel.textContent = "Invalid message received from Fay";
  });
  client.connect();
}

startFayClient().catch((error) => {
  stateLabel.textContent = `Configuration error: ${error.message}`;
});

const samples = new Uint8Array(128);
const clock = new THREE.Clock();

function resize() {
  const width = canvas.clientWidth;
  const height = canvas.clientHeight;
  renderer.setSize(width, height, false);
  camera.aspect = width / Math.max(height, 1);
  camera.updateProjectionMatrix();
}

function animate() {
  resize();
  const elapsed = clock.getElapsedTime();
  const breathing = Math.sin(elapsed * 1.35) * 0.012;
  avatar.position.y = breathing;
  avatar.rotation.y = Math.sin(elapsed * 0.35) * 0.035;

  if (analyser && audioElement && !audioElement.paused) {
    analyser.getByteTimeDomainData(samples);
    let sum = 0;
    for (const sample of samples) {
      const normalized = (sample - 128) / 128;
      sum += normalized * normalized;
    }
    const rms = Math.sqrt(sum / samples.length);
    speakingEnergy += (Math.min(rms * 7, 1) - speakingEnergy) * 0.32;
  } else {
    speakingEnergy *= 0.78;
  }
  mouth.scale.y = 0.25 + speakingEnergy * 3.2;

  renderer.render(scene, camera);
  requestAnimationFrame(animate);
}

window.addEventListener("beforeunload", () => client?.close());
animate();
