# Fay Spark avatar renderer

This is the Spark-native display client for Fay. It connects directly to the
avatar WebSocket on port `10002`, plays Fay's generated WAV files, and exposes
audio energy to the 3D scene for initial mouth movement.

The current geometric head is a diagnostic fixture, not the final character.
It proves WebGL rendering, WebSocket delivery, audio playback, and animation on
the Spark before a free rigged female GLB is selected and integrated.

## Build and run

```bash
cd avatar/web
npm ci
npm run build
FAY_HTTP_BASE=http://<spark-tailnet-ip>:5000 npm start
```

Open `http://127.0.0.1:5173` in Chromium on the Spark. The server derives the
avatar WebSocket address from `FAY_HTTP_BASE`. Override it with `FAY_WS_URL` or
a query parameter when needed:

```text
http://127.0.0.1:5173/?ws=ws://<spark-tailnet-ip>:10002
```

## Integration order

1. Validate WebGL, Fay connection, WAV playback, and amplitude mouth movement.
2. Replace the diagnostic mesh with a licensed free female GLB.
3. Map named facial morph targets to visemes and emotion signals.
4. Add idle, blink, listening, speaking, and gesture animation states.
5. Add a user service and Chromium kiosk launcher on the Spark.
6. Run an extended reconnect and playback-order test.
