```python
#!/usr/bin/env python3
"""
Aegis_RAT_Simulator.py
Safe Telemetry Generator for SIEM Testing (PyInstaller RAT Persistence)
Author: GHOST BREACH Threat Labs
Requires: pywin32 (pip install pywin32)
"""

import argparse
import logging
import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone

try:
    import win32evtlogutil
    import win32evtlog
except ImportError:
    print("[!] ERROR: pywin32 module not found. Install via 'pip install pywin32'")
    sys.exit(1)

# Configure strict logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

class TelemetrySimulator:
    def __init__(self, app_name: str = "Aegis_SIEM_Simulator"):
        self.app_name = app_name
        self._register_event_source()

    def _register_event_source(self):
        """Registers a custom event source in the Windows Registry for safe logging."""
        try:
            import win32api
            import win32con
            import win32security
            key_path = f"SYSTEM\\CurrentControlSet\\Services\\EventLog\\Application\\{self.app_name}"
            win32api.RegCreateKey(win32con.HKEY_LOCAL_MACHINE, key_path)
            logger.info(f"Registered custom Event Source: {self.app_name}")
        except Exception as e:
            logger.warning(f"Could not register registry key (Run as Admin for full integration): {e}")

    def generate_xml_7045(self) -> str:
        """Generates exact XML schema for Event ID 7045 (Service Control Manager)."""
        timestamp = datetime.now(timezone.utc).isoformat()
        
        xml_data = f"""<Event xmlns="http://schemas.microsoft.com/win/2004/08/events/event">
  <System>
    <Provider Name="Service Control Manager" Guid="{{555908d1-a6d7-4695-8e1e-26931d2012f4}}" EventSourceName="Service Control Manager"/>
    <EventID Qualifiers="16384">7045</EventID>
    <Version>0</Version>
    <Level>4</Level>
    <Task>0</Task>
    <Opcode>0</Opcode>
    <Keywords>0x8080000000000000</Keywords>
    <TimeCreated SystemTime="{timestamp}"/>
    <EventRecordID>112345</EventRecordID>
    <Correlation/>
    <Execution ProcessID="840" ThreadID="1200"/>
    <Channel>System</Channel>
    <Computer>AEGIS-RTM-MGR01.aegis-logistics.local</Computer>
    <Security UserID="S-1-5-18"/>
  </System>
  <EventData>
    <Data Name="ServiceName">Aegis System Update Service</Data>
    <Data Name="ImagePath">C:\\ProgramData\\Aegis\\AegisSys.exe</Data>
    <Data Name="ServiceType">user mode service</Data>
    <Data Name="StartType">auto start</Data>
    <Data Name="AccountName">LocalSystem</Data>
  </EventData>
</Event>"""
        return xml_data

    def write_event(self, event_id: int, category: int, strings: list, xml_payload: str):
        """Writes the simulated event to the Application log and dumps XML for direct SIEM ingestion."""
        try:
            win32evtlogutil.ReportEvent(
                self.app_name,
                event_id,
                eventCategory=category,
                eventType=win32evtlog.EVENTLOG_INFORMATION_TYPE,
                strings=strings,
                data=xml_payload.encode('utf-8')
            )
            logger.info(f"Successfully wrote mock Event ID {event_id} to Application Hive.")
            logger.info(f"Raw XML generated for SIEM JSON/XML collector:\n{xml_payload}\n")
        except Exception as e:
            logger.error(f"Failed to write event log: {e}")

def main():
    parser = argparse.ArgumentParser(description="Aegis SIEM Telemetry Simulator")
    parser.add_argument('--simulate-7045', action='store_true', help="Simulate RAT Service Installation (EID 7045)")
    args = parser.parse_args()

    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit(1)

    simulator = TelemetrySimulator()

    if args.simulate_7045:
        logger.info("Initiating simulation: EID 7045 (Service Control Manager)")
        xml_payload = simulator.generate_xml_7045()
        event_strings = [
            "Aegis System Update Service",
            "C:\\ProgramData\\Aegis\\AegisSys.exe",
            "user mode service",
            "auto start",
            "LocalSystem"
        ]
        simulator.write_event(event_id=7045, category=1, strings=event_strings, xml_payload=xml_payload)

if __name__ == "__main__":
    main()
