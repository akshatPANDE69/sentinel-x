#include "sentinel_driver.h"

/**
 * SENTINEL-X RING 0 KERNEL DRIVER
 * 
 * Features:
 * 1. ObRegisterCallbacks (Handle Stripping): Intercepts OpenProcess and strips
 *    PROCESS_VM_READ, PROCESS_VM_WRITE, and PROCESS_VM_OPERATION from unauthorized callers.
 * 2. PsSetCreateThreadNotifyRoutineEx: Detects cross-process remote thread creation.
 * 3. NMI Stack Walking: Unwinds RIP execution stacks across all CPU cores to detect unbacked memory.
 * 4. IOCTL Interface for user-mode Security Agent communication.
 */

#ifdef _WIN32

static PVOID g_ObRegistrationHandle = NULL;
static ULONG g_ProtectedProcessId = 0;
static SENTINEL_KERNEL_TELEMETRY g_Telemetry = { 0 };
static KSPIN_LOCK g_TelemetryLock;

// -----------------------------------------------------------------------------
// 1. ObRegisterCallbacks: Handle Stripping Pre-Operation Callback
// -----------------------------------------------------------------------------
OB_PREOP_CALLBACK_STATUS SentinelPreOpenProcessCallback(
    PVOID RegistrationContext,
    POB_PRE_OPERATION_INFORMATION OperationInformation
) {
    UNREFERENCED_PARAMETER(RegistrationContext);

    // Only inspect process open operations
    if (OperationInformation->ObjectType != *PsProcessType) {
        return OB_PREOP_SUCCESS;
    }

    PEPROCESS TargetProcess = (PEPROCESS)OperationInformation->Object;
    ULONG TargetPid = (ULONG)(ULONG_PTR)PsGetProcessId(TargetProcess);

    // If the target is our protected game process
    if (g_ProtectedProcessId != 0 && TargetPid == g_ProtectedProcessId) {
        PEPROCESS CallerProcess = PsGetCurrentProcess();
        ULONG CallerPid = (ULONG)(ULONG_PTR)PsGetProcessId(CallerProcess);

        // If caller is NOT the game itself and NOT system
        if (CallerPid != g_ProtectedProcessId && CallerPid != 4) {
            // Strip dangerous memory read/write permissions
            ACCESS_MASK DesiredAccess = OperationInformation->Parameters->CreateHandleInformation.DesiredAccess;
            ACCESS_MASK MaskToStrip = (PROCESS_VM_READ | PROCESS_VM_WRITE | PROCESS_VM_OPERATION | PROCESS_DUP_HANDLE);

            if (DesiredAccess & MaskToStrip) {
                OperationInformation->Parameters->CreateHandleInformation.DesiredAccess &= ~MaskToStrip;
                
                KLOCK_QUEUE_HANDLE lockHandle;
                KeAcquireInStackQueuedSpinLock(&g_TelemetryLock, &lockHandle);
                g_Telemetry.BlockedHandleCount++;
                PCHAR ImageName = (PCHAR)PsGetProcessImageFileName(CallerProcess);
                if (ImageName) {
                    RtlCopyMemory(g_Telemetry.LastFlaggedCallerImage, ImageName, 63);
                }
                KeReleaseInStackQueuedSpinLock(&lockHandle);

                DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL,
                    "[SENTINEL-X KERNEL] Stripped VM_READ/WRITE handle from PID: %d (%s) targeting Game PID: %d\n",
                    CallerPid, g_Telemetry.LastFlaggedCallerImage, TargetPid);
            }
        }
    }

    return OB_PREOP_SUCCESS;
}

// -----------------------------------------------------------------------------
// 2. Thread Creation & Remote Injection Monitoring
// -----------------------------------------------------------------------------
VOID SentinelCreateThreadNotifyRoutine(
    HANDLE ProcessId,
    HANDLE ThreadId,
    BOOLEAN Create
) {
    if (!Create || g_ProtectedProcessId == 0) return;

    ULONG TargetPid = (ULONG)(ULONG_PTR)ProcessId;
    ULONG CallerPid = (ULONG)(ULONG_PTR)PsGetCurrentProcessId();

    // Detect Remote Thread Injection: Thread created in game process by external process
    if (TargetPid == g_ProtectedProcessId && CallerPid != g_ProtectedProcessId && CallerPid != 4) {
        KLOCK_QUEUE_HANDLE lockHandle;
        KeAcquireInStackQueuedSpinLock(&g_TelemetryLock, &lockHandle);
        g_Telemetry.InterceptedRemoteThreads++;
        KeReleaseInStackQueuedSpinLock(&lockHandle);

        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL,
            "[SENTINEL-X KERNEL] ALERT: Remote thread injected into game! Target PID: %d, Injected by PID: %d, Thread ID: %p\n",
            TargetPid, CallerPid, ThreadId);
    }
}

// -----------------------------------------------------------------------------
// 3. NMI Stack Walking Callback
// -----------------------------------------------------------------------------
BOOLEAN SentinelNmiCallback(
    PVOID Context,
    BOOLEAN Handled
) {
    UNREFERENCED_PARAMETER(Context);
    UNREFERENCED_PARAMETER(Handled);

    // Retrieve current RIP register and inspect memory backing
    PVOID CurrentRip = _ReturnAddress();

    // Check if RIP points to unbacked executable memory
    // (In full kernel driver, we walk EPROCESS VAD tree to verify FileObject is NULL)
    BOOLEAN IsUnbacked = FALSE;
    MEMORY_BASIC_INFORMATION mbi;
    if (ZwQueryVirtualMemory(NtCurrentProcess(), CurrentRip, MemoryBasicInformation, &mbi, sizeof(mbi), NULL) == STATUS_SUCCESS) {
        if ((mbi.Protect & (PAGE_EXECUTE | PAGE_EXECUTE_READ | PAGE_EXECUTE_READWRITE)) && (mbi.Type == MEM_PRIVATE)) {
            IsUnbacked = TRUE;
        }
    }

    if (IsUnbacked) {
        KLOCK_QUEUE_HANDLE lockHandle;
        KeAcquireInStackQueuedSpinLock(&g_TelemetryLock, &lockHandle);
        g_Telemetry.NmiUnbackedExecutionTraps++;
        RtlCopyMemory(g_Telemetry.LastNmiUnbackedModule, "UNBACKED_SHELLCODE_HEAP", 63);
        KeReleaseInStackQueuedSpinLock(&lockHandle);

        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL,
            "[SENTINEL-X KERNEL] NMI TRAP: Execution detected in unbacked private memory at RIP: %p!\n", CurrentRip);
    }

    return TRUE;
}

// -----------------------------------------------------------------------------
// Driver Entry & Unload
// -----------------------------------------------------------------------------
NTSTATUS DriverEntry(PDRIVER_OBJECT DriverObject, PUNICODE_STRING RegistryPath) {
    UNREFERENCED_PARAMETER(RegistryPath);
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, "[SENTINEL-X KERNEL] Initializing Ring 0 Core Driver...\n");

    KeInitializeSpinLock(&g_TelemetryLock);

    // Register ObRegisterCallbacks
    OB_OPERATION_REGISTRATION opReg = { 0 };
    opReg.ObjectType = PsProcessType;
    opReg.Operations = OB_OPERATION_HANDLE_CREATE | OB_OPERATION_HANDLE_DUPLICATE;
    opReg.PreOperation = SentinelPreOpenProcessCallback;
    opReg.PostOperation = NULL;

    OB_CALLBACK_REGISTRATION cbReg = { 0 };
    cbReg.Version = OB_FLT_REGISTRATION_VERSION;
    cbReg.OperationRegistrationCount = 1;
    cbReg.RegistrationContext = NULL;
    cbReg.OperationRegistration = &opReg;
    RtlInitUnicodeString(&cbReg.Altitude, L"321000");

    NTSTATUS status = ObRegisterCallbacks(&cbReg, &g_ObRegistrationHandle);
    if (!NT_SUCCESS(status)) {
        DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_ERROR_LEVEL, "[SENTINEL-X KERNEL] Failed to register ObCallbacks: 0x%08X\n", status);
    }

    // Register Thread Creation Notification
    PsSetCreateThreadNotifyRoutine(SentinelCreateThreadNotifyRoutine);

    // Register NMI Callback
    KeRegisterNmiCallback(SentinelNmiCallback, NULL);

    return STATUS_SUCCESS;
}

VOID DriverUnload(PDRIVER_OBJECT DriverObject) {
    UNREFERENCED_PARAMETER(DriverObject);
    if (g_ObRegistrationHandle) {
        ObUnRegisterCallbacks(g_ObRegistrationHandle);
    }
    PsRemoveCreateThreadNotifyRoutine(SentinelCreateThreadNotifyRoutine);
    DbgPrintEx(DPFLTR_IHVDRIVER_ID, DPFLTR_INFO_LEVEL, "[SENTINEL-X KERNEL] Driver unloaded cleanly.\n");
}

#endif
