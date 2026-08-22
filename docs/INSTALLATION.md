# 📦 Installation Guide

## Prerequisites

- **macOS:** macOS 12+ (Apple Silicon or Intel), Python 3.10+, Rust 1.80+ (optional: auto-installed), Clang / C++17.
- **Windows:** Windows 10/11 x64, Python 3.10+, Visual Studio C++ Build Tools or Rust toolchain.
- **Linux:** Ubuntu 22.04+ / Debian 12+, Python 3.10+, GCC/Clang, Rust toolchain.

## macOS / Linux Installation

```bash
# Clone and install dependencies & compile Rust Core:
./install.sh

# Start the Security Agent and Local Server:
./run_agent.sh
```

## Windows Installation

```powershell
# In PowerShell (Administrator):
.\install.ps1

# Start the agent:
.\run_agent.bat
```

## Local Console Access

- **HTTP Console:** `http://127.0.0.1:8080/`
- **HTTPS Console:** `https://127.0.0.1:8443/`
