# Installation and standalone execution

`k34cover` supports Python 3.9 and later. Current Ubuntu and Debian releases
mark their system Python installation as *externally managed* under PEP 668.
This is intentional distribution policy: `pip` is prevented from modifying
packages owned by the operating system.

Consequently, a command such as

```bash
python3 -m pip install -e .
```

may fail with `error: externally-managed-environment` when it is run outside a
virtual environment. Do **not** solve this by adding `--break-system-packages`;
that option bypasses the operating-system safeguard and is unnecessary for
`k34cover`.

## 1. Standalone release executable

For ordinary command-line use, the simplest release artifact is
`k34cover-0.4.3.pyz`. It is a self-contained Python zip application containing
`k34cover`.  The active generator has no third-party runtime dependencies.

```bash
chmod +x k34cover-0.4.3.pyz
./k34cover-0.4.3.pyz --lb 7 --ub 60 --output report.txt
```

Alternatively:

```bash
python3 k34cover-0.4.3.pyz --lb 7 --ub 60 --output report.txt
```

No installation, virtual environment, `pip`, or administrator access is needed.
A Python 3.9+ interpreter must be available on the machine. Because the release
is a Python zip application rather than a native Linux binary, the same file is
portable across CPU architectures and Linux distributions supported by Python.

The optional historical `galois`-based projective-plane helper is not bundled
in the standalone executable because it is not used by the active generator.

## 2. pipx installation

`pipx` is the preferred way to install `k34cover` as a persistent command-line
application on Ubuntu/Debian. `pipx` creates a dedicated virtual environment
without exposing it to the user.

```bash
sudo apt install pipx
pipx ensurepath
pipx install .
```

For a cloned repository, run the last command in the repository root. If the
shell reports that the PATH was changed, reopen the terminal before invoking
`k34cover`.

To remove the installation later:

```bash
pipx uninstall k34cover
```

## 3. Development environment

Developers should use a project-local virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
```

On Ubuntu/Debian, install the venv support package if necessary:

```bash
sudo apt install python3-venv
```

The environment can be left with:

```bash
deactivate
```

The `.venv/` directory is local build state and should not be committed.

## Why not `--break-system-packages`?

PEP 668 protects the Python installation maintained by the operating system.
Using `--break-system-packages` allows `pip` to write into that managed
installation and can create conflicts with packages installed by `apt`.
`k34cover` does not require that override. Use the standalone `.pyz`, `pipx`,
or a virtual environment instead.
