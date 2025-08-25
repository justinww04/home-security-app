# Stub for Phase 2 (push/SMS). For now we just print to console.
def notify(label: str, confidence: float | None):
    if confidence is not None:
        print(f"[ALERT] {label} detected (conf={confidence:.2f})")
    else:
        print(f"[ALERT] {label} detected")