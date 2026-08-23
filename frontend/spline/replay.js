// Neurobrain X - Attack Replay Logic

class AttackReplay {
    constructor(onStateChange) {
        this.events = [];
        this.currentIndex = -1;
        this.isPlaying = false;
        this.timer = null;
        this.onStateChange = onStateChange; // callback(currentIndex, activeEvent)
        this.playbackSpeedMs = 1000;
    }

    loadIncident(incident) {
        this.stop();
        if (incident && incident.best_path && incident.events) {
            // Replay only events related to the incident nodes
            const pathNodes = new Set(incident.best_path.nodes);
            this.events = incident.events.filter(e => pathNodes.has(e.source) || pathNodes.has(e.destination));
            this.events.sort((a,b) => a.event_time - b.event_time);
            this.currentIndex = -1;
        } else {
            this.events = [];
            this.currentIndex = -1;
        }
        this._notify();
    }

    play() {
        if (this.events.length === 0) return;
        if (this.currentIndex >= this.events.length - 1) this.currentIndex = -1;
        this.isPlaying = true;
        this._step();
    }

    pause() {
        this.isPlaying = false;
        if (this.timer) clearTimeout(this.timer);
    }

    stop() {
        this.pause();
        this.currentIndex = -1;
        this._notify();
    }

    next() {
        if (this.events.length === 0) return;
        this.currentIndex = Math.min(this.currentIndex + 1, this.events.length - 1);
        this._notify();
    }
    
    reset() {
        this.pause();
        this.currentIndex = -1;
        this._notify();
    }

    _step() {
        if (!this.isPlaying) return;
        this.currentIndex++;
        this._notify();
        
        if (this.currentIndex >= this.events.length - 1) {
            this.isPlaying = false;
        } else {
            this.timer = setTimeout(() => this._step(), this.playbackSpeedMs);
        }
    }

    _notify() {
        const activeEvent = this.currentIndex >= 0 && this.currentIndex < this.events.length 
            ? this.events[this.currentIndex] 
            : null;
        this.onStateChange({
            currentIndex: this.currentIndex,
            totalEvents: this.events.length,
            activeEvent,
            isPlaying: this.isPlaying,
            events: this.events
        });
    }
}

window.AttackReplay = AttackReplay;
