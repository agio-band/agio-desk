import subprocess
import threading
import signal
import time
import logging
import os
from typing import Optional, Dict, List, Union

import psutil


class ProcessWrapper:
    def __init__(self, name: str, command: list[str], restart: bool = True,
                 cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None):
        self.name = name
        self.command = command
        self.process: Optional[subprocess.Popen] = None
        self._psutil_proc: Optional[psutil.Process] = None
        self.lock = threading.Lock()
        self._should_run = restart
        # Store initial cwd and env
        self._cwd = cwd
        self._env = env if env is not None else {}

    def start(self, cwd_override: Optional[str] = None, env_override: Optional[Dict[str, str]] = None):
        with self.lock:
            if self.process and self.process.poll() is None:
                logging.info(f"Process '{self.name}' is already running.")
                return

            # Update stored cwd if an override is provided
            if cwd_override is not None:
                self._cwd = cwd_override

            # Prepare the environment for the subprocess
            current_env = os.environ.copy()
            current_env.update(self._env) # Apply current stored environment
            if env_override:
                current_env.update(env_override) # Apply provided overrides
                self._env.update(env_override) # Update stored environment with overrides

            logging.info(f"Starting process '{self.name}': {self.command} in CWD: {self._cwd} with ENV updates: {env_override}")
            try:
                self.process = subprocess.Popen(
                    self.command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=self._cwd, # Use the potentially updated self._cwd
                    env=current_env
                )
                # self._should_run = True
                try:
                    self._psutil_proc = psutil.Process(self.process.pid)
                except psutil.NoSuchProcess:
                    self._psutil_proc = None
                threading.Thread(target=self._log_output, daemon=True).start()
            except FileNotFoundError:
                logging.error(f"Error: Command '{self.command[0]}' not found for process '{self.name}'.")
                self.process = None
                self._psutil_proc = None
                print('restart OFF')
                self._should_run = False
            except Exception as e:
                logging.error(f"Error starting process '{self.name}': {e}")
                self.process = None
                self._psutil_proc = None
                print('restart OFF 2')
                self._should_run = False

    def restart(self, cwd_override: Optional[str] = None, env_override: Optional[Dict[str, str]] = None):
        logging.info(f"Restarting process '{self.name}'...")
        self.stop(_soft=True)
        time.sleep(0.2)
        self.start(cwd_override=cwd_override, env_override=env_override)

    def stop(self, _soft=False):
        with self.lock:
            if not _soft:
                self._should_run = False
            if self.process is None:
                logging.info(f"Process '{self.name}' is not running.")
                return
            if self.process.poll() is None:
                logging.info(f"Stopping process '{self.name}'...")
                self.process.terminate()
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    logging.warning(f"Force killing process '{self.name}'...")
                    self.process.kill()
                    self.process.wait()
            else:
                logging.info(f"Process '{self.name}' is already stopped.")
            self.process = None
            self._psutil_proc = None

    def _log_output(self):
        assert self.process is not None
        for line in self.process.stdout:
            logging.info(f"[{self.name} STDOUT] {line.decode(errors='ignore').strip()}")
        for line in self.process.stderr:
            logging.error(f"[{self.name} STDERR] {line.decode(errors='ignore').strip()}")

    def is_running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def info(self) -> dict:
        return {
            "name": self.name,
            "pid": self.pid(),
            "running": self.is_running(),
            "cpu_percent": self.cpu_usage(),
            "memory_mb": self.mem_usage(),
            "auto_restart": self._should_run,
            "current_cwd": self._cwd, # Include current cwd in info
            "current_env": self._env # Include current env in info (careful with sensitive data)
        }

    def should_run(self) -> bool:
        return self._should_run

    def pid(self) -> Optional[int]:
        if self.process:
            return self.process.pid
        return None

    def cpu_usage(self) -> Optional[float]:
        if self._psutil_proc and self.is_running():
            try:
                return self._psutil_proc.cpu_percent(interval=0.1)
            except psutil.NoSuchProcess:
                self._psutil_proc = None
                return None
        return None

    def mem_usage(self) -> Optional[float]:
        if self._psutil_proc and self.is_running():
            try:
                return self._psutil_proc.memory_info().rss / (1024 ** 2)
            except psutil.NoSuchProcess:
                self._psutil_proc = None
                return None
        return None


class ProcessHub:
    def __init__(self):
        self._processes: Dict[str, ProcessWrapper] = {}
        self._lock = threading.Lock()
        self._running = True
        threading.Thread(target=self._monitor_processes, daemon=True).start()

    def register_process(self, name: str, command: list[str], restart: bool = False,
                         cwd: Optional[str] = None, env: Optional[Dict[str, str]] = None):
        with self._lock:
            if name in self._processes:
                raise ValueError(f"Process '{name}' is already registered.")
            self._processes[name] = ProcessWrapper(name, command, restart, cwd, env)
            logging.info(f"Registered process '{name}'.")

    def unregister_process(self, name: str):
        with self._lock:
            if name in self._processes:
                del self._processes[name]
                logging.info(f"Unregistered process '{name}'.")

    def start_process(self, name: str):
        with self._lock:
            process = self._processes.get(name)
            if not process:
                raise ValueError(f"Process '{name}' not found.")
            process.start()

    def stop_process(self, name: str):
        with self._lock:
            process = self._processes.get(name)
            if not process:
                raise ValueError(f"Process '{name}' not found.")
            process.stop()

    def restart_process(self, name: str, cwd: Optional[str] = None, env_override: Optional[Dict[str, str]] = None):
        """
        Restarts a registered process, optionally setting a new permanent working directory
        and/or overriding environment variables.
        The `env_override` dictionary will update (not replace) the existing environment.
        The `cwd` will become the new default working directory for the process.
        """
        with self._lock:
            process = self._processes.get(name)
            if not process:
                raise ValueError(f"Process '{name}' not found.")
            process.restart(cwd_override=cwd, env_override=env_override)

    def is_process_alive(self, name: str) -> bool:
        with self._lock:
            process = self._processes.get(name)
            return process.is_running() if process else False

    def stop_all(self):
        with self._lock:
            for name, process in self._processes.items():
                try:
                    process.stop()
                except Exception as e:
                    logging.error(f"Error stopping '{name}': {e}")

    def shutdown(self):
        if self._running:
            logging.info("Shutting down all processes...")
            self._running = False
            self.stop_all()

    def is_running(self):
        return self._running

    def get_stats(self) -> Dict[str, dict]:
        with self._lock:
            return {name: p.info() for name, p in self._processes.items()}

    def _monitor_processes(self):
        while self._running:
            with self._lock:
                for name, process in self._processes.items():
                    if process.should_run() and not process.is_running():
                        logging.warning(f"Process '{name}' died unexpectedly. Restarting with current configuration...")
                        # Restart without new overrides, using the last saved config
                        process.restart()
            time.sleep(3)

