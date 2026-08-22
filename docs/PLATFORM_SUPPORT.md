# 🌍 Platform Support & Reality Matrix

| Platform | User-Space Agent | Rust Core | Native SIMD | Kernel Driver | Verification Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **macOS (Apple Silicon)** | ✅ | ✅ | ARM NEON | Simulated | **`VERIFIED_RUNTIME`** |
| **macOS (Intel)** | ✅ | ✅ | AVX2 | Simulated | **`VERIFIED_RUNTIME`** |
| **Windows 10 / 11** | ✅ | ✅ | AVX2 | Source Available | **`VERIFIED_RUNTIME (User)` / `SOURCE_ONLY (Kernel)`** |
| **Linux (Ubuntu/Debian)** | ✅ | ✅ | AVX2 | Simulated | **`VERIFIED_TEST`** |
| **Retro Hardware (8-bit)** | ❌ | ❌ | ❌ | ❌ | **`NOT_SUPPORTED (Requires Emulator Bridge)`** |
