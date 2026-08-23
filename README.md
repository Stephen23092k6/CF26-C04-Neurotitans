# Neurobrain X — Full 12-Hour Prototype

## Run
```bash
pip install -r requirements.txt
uvicorn app.api:app --host 0.0.0.0 --port 8000
```
Open http://localhost:8000

## Tests
```bash
pytest -q
```

## Benchmark
```bash
python benchmarks/run_benchmark.py
```

## Round-1 demo sequence
1. Open the SOC.
2. Show the graph and healthy state.
3. Click **Reconstruct Controlled Attack**.
4. Explain the candidate path, score and evidence.
5. Open Resilience Lab.
6. Introduce missing/delayed/duplicate telemetry.
7. Run the benchmark.
8. Explain the research question and limitations.

Important: benchmark outputs must be treated as measured prototype results only after executing the harness; do not invent or pre-claim real-world performance.
