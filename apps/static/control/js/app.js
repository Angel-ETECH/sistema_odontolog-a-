document.querySelectorAll('.form-eliminar').forEach(formulario => {
    formulario.addEventListener('submit', evento => {
        if (!window.confirm('¿Deseas eliminar este registro? Esta acción no se puede deshacer.')) evento.preventDefault();
    });
});
document.querySelectorAll('[data-imprimir]').forEach(boton => {
    boton.addEventListener('click', () => window.print());
});

// Hora local del consultorio, aunque el navegador use otra zona horaria.
function actualizarHora() {
    const hora = new Intl.DateTimeFormat('es-PE', {
        timeZone: 'America/Lima', hour: '2-digit', minute: '2-digit'
    }).format(new Date());
    document.querySelectorAll('[data-reloj]').forEach(reloj => {
        reloj.textContent = `${hora} · Lima`;
    });
}
if (document.querySelector('[data-reloj]')) {
    actualizarHora();
    setInterval(actualizarHora, 60000);
}

document.querySelectorAll('.estado').forEach(etiqueta => {
    etiqueta.dataset.estado = etiqueta.textContent.trim();
});

// Mantener la cifra final disponible cuando se prefiere reducir el movimiento.
if (!window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    document.querySelectorAll('[data-contador]').forEach(elemento => {
        const total = Number(elemento.dataset.contador);
        if (!Number.isFinite(total) || total === 0) return;
        const comienzo = performance.now();
        function animar(ahora) {
            const avance = Math.min((ahora - comienzo) / 650, 1);
            elemento.textContent = Math.round(total * (1 - Math.pow(1 - avance, 3)));
            if (avance < 1) requestAnimationFrame(animar);
        }
        requestAnimationFrame(animar);
    });
}
