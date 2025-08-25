export interface EventOut {
  id: number;
  timestamp: string;
  label: string;
  confidence?: number;
  camera: string;
  snapshot_path: string;
}
