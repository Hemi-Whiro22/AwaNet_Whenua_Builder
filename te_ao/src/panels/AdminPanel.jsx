import { useState } from "react";

export default function AdminPanel() {
  const [customer, setCustomer] = useState("");
  const [key, setKey] = useState("");
  const [error, setError] = useState("");

  async function createKey() {
    setError("");
    setKey("");
    if (!customer.trim()) {
      setError("Customer name required.");
      return;
    }
    try {
      const res = await fetch(
        `http://localhost:8000/admin/pro/generate_key?customer_name=${encodeURIComponent(
          customer
        )}`,
        {
          method: "POST",
        }
      );
      const data = await res.json();
      if (!res.ok) {
        setError(data.detail || "Error creating key.");
        return;
      }
      setKey(data.api_key || "Error");
    } catch (e) {
      setError(String(e));
    }
  }

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">Admin / Pro Tier</h2>

      <input
        className="w-full p-4 bg-stone rounded mb-4"
        placeholder="Customer name…"
        value={customer}
        onChange={(e) => setCustomer(e.target.value)}
      />

      <button
        onClick={createKey}
        className="px-6 py-3 bg-awa rounded shadow-lg"
      >
        Create API Key
      </button>

      {error && (
        <div className="mt-4 p-3 bg-red-900 rounded">
          <p>{error}</p>
        </div>
      )}

      {key && (
        <div className="mt-6 p-4 bg-stone rounded">
          <p className="font-bold mb-2">Generated Key:</p>
          <pre>{key}</pre>
        </div>
      )}
    </div>
  );
}
