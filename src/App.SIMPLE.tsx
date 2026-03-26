// VERSION ULTRA-SIMPLIFICADA PARA DIAGNÓSTICO
// Esta versión NO tiene AuthContext, NO tiene rutas, NADA que pueda causar loops

function App() {
  console.log('🚀 App.SIMPLE.tsx cargando...');
  
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '10px',
        boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
        textAlign: 'center'
      }}>
        <h1 style={{ color: '#667eea', margin: '0 0 20px 0' }}>
          ✅ React Funcionando
        </h1>
        <p style={{ color: '#666', fontSize: '18px' }}>
          Si ves este mensaje, React está cargando correctamente.
        </p>
        <p style={{ color: '#10b981', fontWeight: 'bold', fontSize: '24px' }}>
          El problema estaba en AuthContext o en las rutas.
        </p>
        <hr style={{ margin: '20px 0' }} />
        <p><strong>Siguiente paso:</strong></p>
        <p>Restaurar el App.tsx original y depurar AuthContext.</p>
      </div>
    </div>
  );
}

export default App;
