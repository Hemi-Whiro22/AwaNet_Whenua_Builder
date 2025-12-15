import { useEffect, useState } from "react";
import { awa } from "./useAwa";

export function useAwaEvents() {
  const [events, setEvents] = useState([]);

  // Disabled auto-polling to prevent hanging on page load
  // useEffect(() => {
  //   const tick = setInterval(async () => {
  //     try {
  //       const res = await awa("/status/full");
  //       setEvents(res ? [res] : []);
  //     } catch {
  //       setEvents([]);
  //     }
  //   }, 2000);

  //   return () => clearInterval(tick);
  // }, []);

  return events;
}
