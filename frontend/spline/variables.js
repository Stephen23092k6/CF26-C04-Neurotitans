// Neurobrain X - Spline Variables Registry
// Spline expects pre-configured variables on the scene. Since we are using a generic scene
// or one that will be wired later, this defines the contract of variable names.

const SplineVars = {
    // Colors
    COLOR_OBSERVED: '#32a8ff',
    COLOR_INFERRED: '#ffae2b',
    COLOR_ANOMALY: '#ff3b5c',
    COLOR_DEFAULT: '#101722',

    nodeVisible: (nodeId) => `node_${nodeId}_visible`,
    nodeColor: (nodeId) => `node_${nodeId}_color`,
    nodeScale: (nodeId) => `node_${nodeId}_scale`,
    
    edgeVisible: (src, dst) => `edge_${src}_${dst}_visible`,
    edgeColor: (src, dst) => `edge_${src}_${dst}_color`,
    edgeDashed: (src, dst) => `edge_${src}_${dst}_dashed`,
    
    anomalyVisible: (nodeId) => `anomaly_${nodeId}_visible`,
    
    // Global state variables
    replayActive: 'replay_active',
    currentFloor: 'current_floor'
};

window.SplineVars = SplineVars;
