import axios from "axios";
import { EventOut } from "./types/EventOut";
import type { ActivePerson } from "./types/ActivePerson";

const BASE_URL = import.meta.env.VITE_API_BASE ?? "http://localhost:8000";

const api = {
  getEvents: async (): Promise<EventOut[]> => {
    const res = await axios.get(`${BASE_URL}/events`);
    return res.data;
  },

  getSnapshot: async (): Promise<Blob> => {
    const res = await axios.get(`${BASE_URL}/snapshot`, { responseType: "blob" });
    return res.data;
  },

  getHealth: async () => {
  await axios.get(`${BASE_URL}/health`);
},

  getPeople: async () => {
    const res = await axios.get(`${BASE_URL}/people`);
    return res.data;
  },

  deletePerson: async (id: number) => {
    await axios.delete(`${BASE_URL}/people/${id}`);
  },

  addPerson: async (name: string) => {
    const res = await axios.post(`${BASE_URL}/enroll/start`, { name });
    return res.data;
  },

  startEnrollment: async (name: string) => {
    const res = await axios.post(`${BASE_URL}/enroll/start`, { name });
    return res.data;
  },

  captureEnrollment: async (session_id: string, angle: string, image_b64: string) => {
    await axios.post(`${BASE_URL}/enroll/capture`, {
      session_id,
      angle,
      image_b64,
    });
  },

  finishEnrollment: async (session_id: string) => {
    await axios.post(`${BASE_URL}/enroll/finish`, { session_id });
  },

  fetchActive: async (): Promise<ActivePerson[]> => {
    const res = await axios.get(`${BASE_URL}/active`);
    return res.data;
  },
};

export const snapshotURL = `${BASE_URL}/snapshot`;
export const videoURL = `${BASE_URL}/video.mjpg`;
export const wsURL = `${BASE_URL.replace(/^http/, "ws")}/ws/events`;

export { api };