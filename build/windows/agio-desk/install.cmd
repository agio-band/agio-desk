@echo off

rem for /f "usebackq delims=" %%p in ("requirements.txt") do uv add %%p

call env.cmd
uv venv --clear
uv sync
uv run python -m init_settings
