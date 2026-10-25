const NOMBRES_TIPO = {
  muro: 'Muro de ladrillo',
  viga: 'Viga de hormigón',
  columna: 'Columna de hormigón',
  contrapiso: 'Contrapiso',
  techo: 'Techo',
  pisos: 'Pisos',
  pintura: 'Pintura'
};

const ETIQUETAS = {
  espesor: 'Espesor', largo: 'Largo', alto: 'Alto', ancho: 'Ancho', superficie: 'Superficie'
};

async function api(url, options = {}) {
  let response;
  try {
    response = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      ...options
    });
  } catch (error) {
    throw new Error('No se pudo conectar con el servidor Python. Ejecuta "python server.py" y abre http://127.0.0.1:8000; no abras index.html directamente.');
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(data.error || 'No fue posible completar la solicitud.');
  return data;
}

function mostrarMensaje(texto, tipo = '') {
  let elemento = document.querySelector('.mensaje');
  if (!elemento) {
    elemento = document.createElement('div');
    elemento.className = 'mensaje';
    const contenedor = document.querySelector('.contenedor');
    contenedor?.prepend(elemento);
  }
  elemento.textContent = texto;
  elemento.className = `mensaje visible ${tipo}`;
  window.scrollTo({ top: 0, behavior: 'smooth' });
}

function textoSeguro(texto) {
  return String(texto).replace(/[&<>'"]/g, caracter => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#039;', '"': '&quot;' }[caracter]));
}

function numeroLocal(valor, decimales = 2) {
  if (Number.isInteger(valor)) return valor.toLocaleString('es-CO');
  return Number(valor).toLocaleString('es-CO', { maximumFractionDigits: decimales });
}

function bloquear(formulario, bloqueado) {
  formulario.querySelectorAll('button').forEach(boton => { boton.disabled = bloqueado; });
}

async function prepararLogin() {
  const formulario = document.querySelector('#login-form');
  if (!formulario) return;
  formulario.addEventListener('submit', async evento => {
    evento.preventDefault();
    bloquear(formulario, true);
    try {
      const data = Object.fromEntries(new FormData(formulario));
      await api('/api/auth/login', { method: 'POST', body: JSON.stringify(data) });
      window.location.href = 'menu.html';
    } catch (error) {
      mostrarMensaje(error.message, 'error');
      bloquear(formulario, false);
    }
  });
}

async function prepararRegistro() {
  const formulario = document.querySelector('#registro-form');
  if (!formulario) return;
  formulario.addEventListener('submit', async evento => {
    evento.preventDefault();
    const data = Object.fromEntries(new FormData(formulario));
    if (data.password !== data.confirmar_password) {
      mostrarMensaje('Las contraseñas no coinciden.', 'error');
      return;
    }
    bloquear(formulario, true);
    try {
      await api('/api/auth/register', { method: 'POST', body: JSON.stringify(data) });
      window.location.href = 'menu.html';
    } catch (error) {
      mostrarMensaje(error.message, 'error');
      bloquear(formulario, false);
    }
  });
}

async function prepararCerrarSesion() {
  document.querySelectorAll('[data-logout]').forEach(boton => {
    boton.addEventListener('click', async evento => {
      evento.preventDefault();
      try { await api('/api/auth/logout', { method: 'POST', body: '{}' }); } finally { window.location.href = 'index.html'; }
    });
  });
}

async function prepararMenu() {
  const historial = document.querySelector('#historial');
  if (!historial) return;
  try {
    const me = await api('/api/auth/me');
    const nombre = document.querySelector('[data-nombre-usuario]');
    if (nombre) nombre.textContent = me.usuario.nombre;
    const data = await api('/api/calculations');
    renderizarHistorial(data.calculos || [], historial);
  } catch (error) {
    if (error.message.includes('sesión')) window.location.href = 'index.html';
    else mostrarMensaje(error.message, 'error');
  }
}

function renderizarHistorial(calculos, contenedor) {
  if (!calculos.length) {
    contenedor.innerHTML = '<div class="vacio">Aún no hay cálculos guardados. Selecciona una opción del menú para comenzar.</div>';
    return;
  }
  const filas = calculos.map(calculo => {
    const fecha = new Date(calculo.created_at).toLocaleString('es-CO');
    return `<tr><td>${textoSeguro(NOMBRES_TIPO[calculo.tipo] || calculo.tipo)}</td><td>${textoSeguro(fecha)}</td><td>${calculo.resultado.items.length} conceptos</td><td><div class="acciones"><a class="boton-mini" href="resultado.html?id=${encodeURIComponent(calculo.id)}">Ver</a><a class="boton-mini" href="${calculo.tipo}.html?edit=${encodeURIComponent(calculo.id)}">Editar</a><button class="boton-mini peligro" data-delete="${textoSeguro(calculo.id)}">Eliminar</button></div></td></tr>`;
  }).join('');
  contenedor.innerHTML = `<div class="tabla-contenedor"><table class="tabla"><thead><tr><th>Tipo</th><th>Fecha</th><th>Resultado</th><th>Acciones</th></tr></thead><tbody>${filas}</tbody></table></div>`;
  contenedor.querySelectorAll('[data-delete]').forEach(boton => boton.addEventListener('click', async () => {
    if (!window.confirm('¿Deseas eliminar este cálculo del historial?')) return;
    try {
      await api(`/api/calculations/${boton.dataset.delete}`, { method: 'DELETE' });
      mostrarMensaje('Cálculo eliminado correctamente.', 'exito');
      prepararMenu();
    } catch (error) { mostrarMensaje(error.message, 'error'); }
  }));
}

function entradasDelFormulario(formulario) {
  const entradas = {};
  new FormData(formulario).forEach((valor, clave) => {
    if (clave === 'tipo') return;
    entradas[clave] = Number(valor);
  });
  return entradas;
}

async function cargarEdicion(formulario) {
  const id = new URLSearchParams(window.location.search).get('edit');
  if (!id) return null;
  try {
    const data = await api(`/api/calculations/${encodeURIComponent(id)}`);
    const calculo = data.calculo;
    Object.entries(calculo.entradas).forEach(([clave, valor]) => {
      const campo = formulario.elements[clave];
      if (!campo) return;
      if (campo.length && campo[0].type === 'radio') {
        [...campo].forEach(opcion => { opcion.checked = Number(opcion.value) === Number(valor); });
      } else campo.value = valor;
    });
    const titulo = formulario.querySelector('h1');
    if (titulo) titulo.insertAdjacentText('afterbegin', 'EDITAR · ');
    return id;
  } catch (error) { mostrarMensaje(error.message, 'error'); return null; }
}

async function prepararCalculo() {
  const formulario = document.querySelector('.calculo-form');
  if (!formulario) return;
  const editId = await cargarEdicion(formulario);
  formulario.addEventListener('submit', async evento => {
    evento.preventDefault();
    const tipo = formulario.dataset.tipo;
    const payload = { tipo, entradas: entradasDelFormulario(formulario) };
    bloquear(formulario, true);
    try {
      const url = editId ? `/api/calculations/${encodeURIComponent(editId)}` : '/api/calculations';
      const method = editId ? 'PUT' : 'POST';
      const data = await api(url, { method, body: JSON.stringify(payload) });
      window.location.href = `resultado.html?id=${encodeURIComponent(data.calculo.id)}`;
    } catch (error) {
      mostrarMensaje(error.message, 'error');
      bloquear(formulario, false);
    }
  });
}

async function prepararResultado() {
  const resultado = document.querySelector('#resultado-dinamico');
  if (!resultado) return;
  const id = new URLSearchParams(window.location.search).get('id');
  if (!id) { resultado.innerHTML = '<p class="vacio">No se indicó un cálculo para mostrar.</p>'; return; }
  try {
    const data = await api(`/api/calculations/${encodeURIComponent(id)}`);
    const calculo = data.calculo;
    const items = calculo.resultado.items.map(item => `<div class="material"><span>${textoSeguro(item.nombre)}</span><strong>${numeroLocal(item.valor)} ${textoSeguro(item.unidad)}</strong></div>`).join('');
    resultado.innerHTML = `<p class="formula">${textoSeguro(calculo.resultado.formula)}</p><h2>${textoSeguro(calculo.resultado.titulo).toUpperCase()}</h2>${items}<div class="botones"><a class="boton secundario" href="${calculo.tipo}.html?edit=${encodeURIComponent(calculo.id)}">EDITAR CÁLCULO</a><a class="boton" href="menu.html">IR AL HISTORIAL</a></div>`;
    const titulo = document.querySelector('[data-titulo-resultado]');
    if (titulo) titulo.textContent = `RESULTADO · ${calculo.resultado.titulo.toUpperCase()}`;
  } catch (error) { mostrarMensaje(error.message, 'error'); }
}

document.addEventListener('DOMContentLoaded', () => {
  prepararLogin();
  prepararRegistro();
  prepararCerrarSesion();
  prepararMenu();
  prepararCalculo();
  prepararResultado();
});
