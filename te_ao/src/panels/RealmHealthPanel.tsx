import { useAwaEvents } from "../hooks/useEvents";

export default function RealmHealthPanel() {
  const events = useAwaEvents();

  return (
    <div className="p-4 text-white">
      <h1 className="text-2xl font-bold mb-4">Realm Health</h1>
      {events.map((e: any, i: number) => (
        <div key={i} className="mb-2 p-2 bg-gray-800 rounded">
          <div>
            <b>Realm:</b> {e.realm}
          </div>
          <div>
            <b>Type:</b> {e.type}
          </div>
          <div>
            <b>Payload:</b> {JSON.stringify(e.payload)}
          </div>
        </div>
      ))}
      {!events.length && <p className="text-slate-300 text-sm">No events yet.</p>}
    </div>
  );
}
