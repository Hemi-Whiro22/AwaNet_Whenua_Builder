import { useState } from 'react'
import './App.css'

function App() {
    const [count, setCount] = useState(0)

    return (
        <div className="App">
            <h1>TemplateRealm Frontend</h1>
            <p>Connected to Te Pō Proxy backend</p>
            <button onClick={() => setCount((count) => count + 1)}>
                Count: {count}
            </button>
        </div>
    )
}

export default App
