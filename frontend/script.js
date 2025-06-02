async function calculateQi() {
    // Valores padrão caso inputs não existam
    const forehand = document.getElementById('forehand')?.value || 5;
    const backhand = document.getElementById('backhand')?.value || 5;
    const fatigue = document.getElementById('fatigue')?.value || 5;
    const pressure = document.getElementById('pressure')?.value || 5;

    try {
        const response = await fetch(
            `http://127.0.0.1:8000/qi/?forehand_spin=${forehand}&backhand_stability=${backhand}&fatigue=${fatigue}&pressure=${pressure}`
        );
        const data = await response.json();
        
        document.getElementById('result').innerHTML = `
            <h3>Resultado</h3>
            <p>Qi Index: <strong>${data.qi_index.toFixed(2)}</strong></p>
            <p style="color: ${data.flow_state ? 'green' : 'red'}">
                ${data.message}
            </p>
        `;
    } catch (error) {
        document.getElementById('result').innerHTML = `
            <p style="color: red;">Erro: API não respondendo. Verifique:</p>
            <ul>
                <li>O servidor está rodando? (START.bat)</li>
                <li>Console (F12) para detalhes</li>
            </ul>
        `;
    }
}