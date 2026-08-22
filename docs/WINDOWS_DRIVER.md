# 🪟 Windows Kernel Driver Specification (`agent/kernel/`)

## Status: `SOURCE ONLY (WINDOWS)`

The KMDF C driver source is located at `agent/kernel/sentinel_driver.c`.

## Features Implemented in Source

1. **`ObRegisterCallbacks`:** Handle stripping of `PROCESS_VM_READ` and `PROCESS_VM_WRITE`.
2. **`PsSetCreateThreadNotifyRoutine`:** Thread injection and foreign thread spawn detection.
3. **`KeRegisterNmiCallback`:** Non-Maskable Interrupt stack walking for unbacked executable code detection.

*Note: On macOS and Linux, these traps are simulated through the multi-vector evidence engine.*
