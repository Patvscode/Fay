const RECONNECT_MIN_MS = 750;
const RECONNECT_MAX_MS = 10_000;

export class FayClient extends EventTarget {
  constructor({ url, username = "User" }) {
    super();
    this.url = url;
    this.username = username;
    this.socket = null;
    this.reconnectDelay = RECONNECT_MIN_MS;
    this.reconnectTimer = null;
    this.closedByUser = false;
  }

  connect() {
    this.closedByUser = false;
    clearTimeout(this.reconnectTimer);
    this.dispatch("status", { state: "connecting" });

    const socket = new WebSocket(this.url);
    this.socket = socket;

    socket.addEventListener("open", () => {
      this.reconnectDelay = RECONNECT_MIN_MS;
      socket.send(JSON.stringify({ Username: this.username, Output: true }));
      this.dispatch("status", { state: "connected" });
    });

    socket.addEventListener("message", (event) => {
      try {
        const message = JSON.parse(event.data);
        this.dispatch("message", message);
      } catch (error) {
        this.dispatch("error", { error });
      }
    });

    socket.addEventListener("close", () => {
      this.dispatch("status", { state: "disconnected" });
      if (!this.closedByUser) this.scheduleReconnect();
    });

    socket.addEventListener("error", () => socket.close());
  }

  close() {
    this.closedByUser = true;
    clearTimeout(this.reconnectTimer);
    this.socket?.close();
  }

  scheduleReconnect() {
    clearTimeout(this.reconnectTimer);
    const wait = this.reconnectDelay;
    this.reconnectDelay = Math.min(this.reconnectDelay * 1.8, RECONNECT_MAX_MS);
    this.reconnectTimer = setTimeout(() => this.connect(), wait);
  }

  dispatch(type, detail) {
    this.dispatchEvent(new CustomEvent(type, { detail }));
  }
}

