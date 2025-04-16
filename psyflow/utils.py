def show_ports():
    """
    List all available serial ports with descriptions.
    """
    import serial.tools.list_ports
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports found.")
    else:
        print("Available serial ports:")
        for i, p in enumerate(ports):
            print(f"[{i}] {p.device} - {p.description}")

