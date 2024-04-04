import './App.css'
import getText from './imports/getText';


function App() {
  return (
    <>
      <h1>{getText('3D print store')}</h1>
      <div className="card">
        <button>
          {getText('Принтирай!')}
        </button>
      </div>
    </>
  )
}

export default App
