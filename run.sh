# uv pip install . --reinstall --cache-dir /WindowsDrive/DriftResearch/lib/python3.10/mhabrar_research/DriftAI/tts_test/uv_cache
# uv run --directory . driftai & fastapi run src/driftai/stt/server.py
uv run --directory . driftai & uv run src/driftai/stt/server.py
