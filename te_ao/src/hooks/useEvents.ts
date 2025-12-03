import { useEffect, useState } from "react";
import { awa } from "./useAwa";

export function useAwaEvents() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const tick = setInterval(async () => {
      const res = await awa("/events");
      setEvents(res);
    }, 2000);

    return () => clearInterval(tick);
  }, []);

  return events;
}
