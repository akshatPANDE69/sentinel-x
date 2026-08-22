#ifndef SENTINEL_DRIVER_H
#define SENTINEL_DRIVER_H

#ifdef _WIN32
#include <ntddk.h>
#include <wdf.h>
#else
// Cross-platform header simulation for non-Windows compile environments
#include <stdint.h>
#include <stddef.h>
typedef uint32_t ULONG;
typedef uint64_t ULONG64;
typedef void* PVOID;
typedef void* HANDLE;
typedef long NTSTATUS;
#define NT_SUCCESS(Status) (((NTSTATUS)(Status)) >= 0)
#define STATUS_SUCCESS ((NTSTATUS)0x00000000L)
#define STATUS_UNSUCCESSFUL ((NTSTATUS)0xC0000001L)
#define STATUS_ACCESS_DENIED ((NTSTATUS)0xC0000022L)
#endif

#define SENTINEL_DEVICE_NAME L"\\Device\\SentinelXCore"
#define SENTINEL_SYM_NAME    L"\\DosDevices\\SentinelXCore"

// IOCTL Definitions
#define IOCTL_SENTINEL_REGISTER_PROCESS CTL_CODE(FILE_DEVICE_UNKNOWN, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_SENTINEL_GET_TELEMETRY    CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_SENTINEL_TRIGGER_NMI      CTL_CODE(FILE_DEVICE_UNKNOWN, 0x803, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_SENTINEL_SCAN_MEMORY      CTL_CODE(FILE_DEVICE_UNKNOWN, 0x804, METHOD_BUFFERED, FILE_ANY_ACCESS)

// Ring 0 Telemetry Record Structure
typedef struct _SENTINEL_KERNEL_TELEMETRY {
    ULONG64 Timestamp;
    ULONG   TargetProcessId;
    ULONG   BlockedHandleCount;
    ULONG   InterceptedRemoteThreads;
    ULONG   NmiUnbackedExecutionTraps;
    ULONG   ScannedPagesCount;
    ULONG   MatchedSignatures;
    double  ScanThroughputGBs;
    char    LastFlaggedCallerImage[64];
    char    LastNmiUnbackedModule[64];
} SENTINEL_KERNEL_TELEMETRY, *PSENTINEL_KERNEL_TELEMETRY;

#endif // SENTINEL_DRIVER_H
