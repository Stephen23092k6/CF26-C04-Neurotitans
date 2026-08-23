// Neurobrain X - Spline Controller
// Bridges vanilla app.js state into the Spline Web Component

class SplineController {
    constructor(viewerId) {
        this.viewer = document.getElementById(viewerId);
        this.app = null;
        this.ready = false;
        
        if (this.viewer) {
            this.viewer.addEventListener('load-complete', () => {
                this.app = this.viewer.spline;
                this.ready = true;
                console.log("Spline Viewer Loaded and Ready");
            });
        }
    }

    _setVar(name, value) {
        if (!this.ready || !this.app) return;
        try {
            this.app.setVariable(name, value);
        } catch (e) {
            // Spline throws if variable doesn't exist in the scene.
            // We swallow this since we are providing generic mappings that a designer might not fully implement.
        }
    }

    updateState(graph, incident) {
        if (!this.ready) return;

        // Collect incident context
        const pathNodes = new Set();
        const inferredEdges = new Set();
        const observedEdges = new Set();
        const anomalies = new Set();

        if (incident && incident.best_path) {
            incident.best_path.nodes.forEach(n => pathNodes.add(n));
            incident.best_path.edges.forEach(e => {
                const edgeKey = `${e.source}_${e.target}`;
                if (e.is_inferred) {
                    inferredEdges.add(edgeKey);
                } else {
                    observedEdges.add(edgeKey);
                }
                
                // Red indicator for identity anomalies
                if (e.inference_reason && e.inference_reason.includes("anomaly") || e.inference_reason.includes("contradiction")) {
                    anomalies.add(e.source);
                    anomalies.add(e.target);
                }
            });
        }

        // Send node updates to Spline
        graph.nodes.forEach(n => {
            const id = n.entity_id;
            const inPath = pathNodes.has(id);
            this._setVar(SplineVars.nodeVisible(id), 1);
            this._setVar(SplineVars.nodeColor(id), inPath ? SplineVars.COLOR_ANOMALY : SplineVars.COLOR_DEFAULT);
            this._setVar(SplineVars.anomalyVisible(id), anomalies.has(id) ? 1 : 0);
        });

        // Send edge updates to Spline
        graph.edges.forEach(e => {
            const src = e.source;
            const dst = e.target;
            const key = `${src}_${dst}`;
            
            this._setVar(SplineVars.edgeVisible(src, dst), 1);
            
            if (inferredEdges.has(key)) {
                this._setVar(SplineVars.edgeColor(src, dst), SplineVars.COLOR_INFERRED);
                this._setVar(SplineVars.edgeDashed(src, dst), 1); // Amber, Dashed
            } else if (observedEdges.has(key)) {
                this._setVar(SplineVars.edgeColor(src, dst), SplineVars.COLOR_OBSERVED);
                this._setVar(SplineVars.edgeDashed(src, dst), 0); // Blue, Solid
            } else {
                this._setVar(SplineVars.edgeColor(src, dst), SplineVars.COLOR_DEFAULT);
                this._setVar(SplineVars.edgeDashed(src, dst), 0); // Default
            }
        });
    }

    updateReplayState(replayState) {
        if (!this.ready) return;
        
        // Highlight active event in 3D
        if (replayState.activeEvent) {
            const ev = replayState.activeEvent;
            // Pulse the source node
            this._setVar(SplineVars.nodeScale(ev.source), 1.5);
            setTimeout(() => this._setVar(SplineVars.nodeScale(ev.source), 1.0), 500);
            
            // Highlight specific anomaly if present in metadata
            if (ev.metadata && (ev.metadata.impossible_context || ev.metadata.spoofed_identity)) {
                this._setVar(SplineVars.anomalyVisible(ev.source), 1);
            }
        }
    }
}

window.SplineController = SplineController;
