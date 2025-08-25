import { useEffect, useState } from "react";
import { ActivePerson } from "../types/ActivePerson";

export default function ActiveTab() {
  const [activePeople, setActivePeople] = useState<ActivePerson[]>([]);

  useEffect(() => {
    const fetchActivePeople = async () => {
      try {
        const res = await fetch("http://localhost:8000/active");
        const data = await res.json();
        setActivePeople(data);
      } catch (err) {
        console.error("Failed to fetch active people:", err);
      }
    };

    fetchActivePeople();
    const interval = setInterval(fetchActivePeople, 2000); // poll every 2 seconds

    return () => clearInterval(interval);
  }, []);

  return (
    <div>
      <h2>Active</h2>
      {activePeople.length === 0 ? (
        <p>No one currently detected.</p>
      ) : (
        <ul>
          {activePeople.map((person) => (
            <li key={person.id}>
  <strong>{person.name}</strong> seen at {new Date(person.first_seen).toLocaleTimeString()}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
