/* main.js — Utilidades compartidas para el Sistema de Taller */

// ── DataTables init ──────────────────────────────────────────────────────────
function destroyDT(selector) {
  if ($.fn.DataTable.isDataTable(selector)) {
    $(selector).DataTable().destroy();
  }
}

function initDT(selector) {
  $(selector).DataTable({
    language: {
      search: 'Buscar:',
      lengthMenu: 'Mostrar _MENU_ registros',
      info: 'Mostrando _START_ a _END_ de _TOTAL_',
      infoEmpty: 'Sin registros',
      zeroRecords: 'No se encontraron resultados',
      paginate: { previous: '‹', next: '›' },
    },
    pageLength: 25,
    order: [],
    responsive: true,
  });
}

// ── Toast / SweetAlert2 notifications ────────────────────────────────────────
function showToast(message, type = 'success') {
  // Errores y warnings → SweetAlert2 (visible, requiere atención)
  if (type === 'danger' || type === 'warning') {
    const swalIcon = type === 'danger' ? 'error' : 'warning';
    const swalTitle = type === 'danger' ? 'Error' : 'Atención';
    const btnColor = type === 'danger' ? '#ef4444' : '#f59e0b';
    Swal.fire({
      icon: swalIcon,
      title: swalTitle,
      text: message,
      confirmButtonColor: btnColor,
      confirmButtonText: 'Entendido',
    });
    return;
  }

  // Success e info → Bootstrap Toast (pequeño, no-intrusivo)
  const colors = { success: '#198754', info: '#0d6efd' };
  const id = 'toast_' + Date.now();
  const icon = type === 'success' ? 'check-circle' : 'info-circle';
  const html = `
    <div id="${id}" class="toast align-items-center border-0 text-white"
         style="background:${colors[type]||colors.info}" role="alert" aria-live="assertive">
      <div class="d-flex">
        <div class="toast-body d-flex align-items-center gap-2">
          <i class="bi bi-${icon}"></i> ${message}
        </div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
      </div>
    </div>`;
  document.getElementById('toastContainer').insertAdjacentHTML('beforeend', html);
  const el = document.getElementById(id);
  const t = new bootstrap.Toast(el, { delay: 3500 });
  t.show();
  el.addEventListener('hidden.bs.toast', () => el.remove());
}

// ── SweetAlert2 utilidades ──────────────────────────────────────────────────
function showError(title, text) {
  Swal.fire({ icon: 'error', title, text, confirmButtonColor: '#ef4444', confirmButtonText: 'Entendido' });
}

function showSuccess(title, text) {
  Swal.fire({ icon: 'success', title, text, confirmButtonColor: '#22c55e', timer: 2000, showConfirmButton: false });
}

function showConfirm(title, text) {
  return Swal.fire({
    icon: 'warning',
    title,
    text,
    showCancelButton: true,
    confirmButtonColor: '#ef4444',
    cancelButtonColor: '#6b7280',
    confirmButtonText: 'Confirmar',
    cancelButtonText: 'Cancelar',
  });
}

// ── Select helper ────────────────────────────────────────────────────────────
function poblarSelect(selectId, items, valueKey, labelFn, blankLabel = '— Seleccionar —') {
  const el = document.getElementById(selectId);
  if (!el) return;
  el.innerHTML = `<option value="">${blankLabel}</option>`;
  items.forEach(item => {
    const opt = document.createElement('option');
    opt.value = item[valueKey];
    opt.textContent = labelFn(item);
    el.appendChild(opt);
  });
}

// ── Fetch helpers ────────────────────────────────────────────────────────────
async function apiGet(endpoint) {
  try {
    const r = await fetch(endpoint);
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.error || err.message || `Error ${r.status}`);
    }
    return r.json();
  } catch (e) {
    if (e.name === 'TypeError') {
      showError('Sin conexión', 'No se pudo conectar con el servidor. Verifica tu conexión.');
    }
    throw e;
  }
}

async function apiPost(endpoint, data) {
  try {
    const r = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({}));
      throw new Error(err.error || err.message || `Error ${r.status}`);
    }
    return r.json();
  } catch (e) {
    if (e.name === 'TypeError') {
      showError('Sin conexión', 'No se pudo conectar con el servidor. Verifica tu conexión.');
    }
    throw e;
  }
}

// ── Fecha hoy YYYY-MM-DD ─────────────────────────────────────────────────────
function hoy() {
  return new Date().toISOString().split('T')[0];
}

// ── Flatpickr default init ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.datepicker').forEach(el => {
    flatpickr(el, { locale: 'es', dateFormat: 'Y-m-d', defaultDate: 'today' });
  });
});
