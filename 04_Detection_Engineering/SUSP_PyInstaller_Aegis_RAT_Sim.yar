import "pe"
import "math"

rule SUSP_PyInstaller_Aegis_RAT_Sim {
    meta:
        description = "Detects high-entropy, PyInstaller-compiled binaries indicative of obfuscated Python RAT payloads used in the Aegis Logistics breach."
        author = "GHOST BREACH Threat Labs"
        date = "2026-05-19"
        reference = "Aegis-IR-2026-05A"
        mitre_attack = "T1027.002 (Software Packing)"
        severity = "High"

    strings:
        // PyInstaller bootloader magic bytes (Archive format)
        $pyi_magic1 = { 4D 45 49 00 12 0B 0B 0B } 
        $pyi_magic2 = "MEI\x00"
        
        // Common strings found in PyInstaller unpacked data
        $s1 = "_MEIPASS" ascii wide
        $s2 = "PyInstaller: Format Message" ascii wide
        $s3 = "Error loading Python DLL" ascii wide

        // Aegis specific indicator (simulated artifact)
        $aegis_ind = "AegisSys.exe" ascii wide nocase

    condition:
        // Must be a valid Windows PE file
        uint16(0) == 0x5A4D and 
        pe.is_pe and
        
        // Must match PyInstaller signatures
        (any of ($pyi_magic*) or 2 of ($s*)) and
        
        // Entropy check: Legitimate PyInstaller apps exist, but
        // > 7.2 entropy across the entire file heavily implies malicious packing/obfuscation.
        math.entropy(0, filesize) >= 7.2 and
        
        // Match specific artifact string if present
        $aegis_ind
}
