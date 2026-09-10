document.addEventListener('DOMContentLoaded', () => {
  const sidebar = document.querySelector('#sidebar');
  const toggle = document.querySelector('#sidebarToggle');
  if (sidebar && toggle) {
    toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', (event) => {
      if (window.innerWidth < 992 && sidebar.classList.contains('open') && !sidebar.contains(event.target) && !toggle.contains(event.target)) sidebar.classList.remove('open');
    });
  }

  document.querySelectorAll('input[type=date]').forEach((input) => {
    input.min = new Date().toISOString().split('T')[0];
  });

  document.querySelectorAll('.js-toast').forEach((link) => {
    link.addEventListener('click', (event) => {
      event.preventDefault();
      showToast('Profile and settings tools are coming soon.');
    });
  });

  document.querySelectorAll('.tabs span, .specialty-strip span').forEach((item) => {
    item.addEventListener('click', () => {
      item.parentElement.querySelectorAll('span').forEach((sibling) => sibling.classList.remove('active'));
      item.classList.add('active');
    });
  });

  const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { displayColors: false, backgroundColor: '#123848', padding: 10, titleFont: { family: 'Poppins' }, bodyFont: { family: 'Poppins' } } },
    scales: { x: { grid: { display: false }, ticks: { color: '#91a4aa', font: { family: 'Poppins', size: 10 } } }, y: { beginAtZero: true, grid: { color: '#edf2f3' }, border: { display: false }, ticks: { color: '#91a4aa', precision: 0, font: { family: 'Poppins', size: 10 } } } }
  };
  const careCanvas = document.querySelector('#careChart');
  if (careCanvas && window.Chart) {
    new Chart(careCanvas, { type: 'line', data: { labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'], datasets: [{ data: [2, 4, 3, 6, 4, 7, Number(careCanvas.dataset.count || 5)], borderColor: '#087f82', backgroundColor: 'rgba(8,127,130,.1)', borderWidth: 2, fill: true, tension: .42, pointRadius: 3, pointBackgroundColor: '#fff', pointBorderColor: '#087f82', pointBorderWidth: 2 }] }, options: chartDefaults });
  }
  const adminCanvas = document.querySelector('#adminChart');
  if (adminCanvas && window.Chart) {
    new Chart(adminCanvas, { type: 'bar', data: { labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'], datasets: [{ data: [18, 24, 22, 31, 27, 36, Number(adminCanvas.dataset.count || 30)], backgroundColor: ['#d4eeee', '#d4eeee', '#d4eeee', '#8bd0d0', '#d4eeee', '#d4eeee', '#087f82'], borderRadius: 6, borderSkipped: false, barThickness: 22 }] }, options: chartDefaults });
  }

  function showToast(message) {
    const toast = document.createElement('div');
    toast.className = 'app-toast';
    Object.assign(toast.style, { position: 'fixed', bottom: '24px', right: '24px', zIndex: '1080', display: 'flex', alignItems: 'center', gap: '10px', padding: '12px 16px', borderRadius: '10px', background: '#123848', color: '#fff', boxShadow: '0 12px 30px rgba(20,54,69,.2)', fontSize: '12px', opacity: '0', transform: 'translateY(8px)', transition: '.25s ease' });
    toast.innerHTML = `<i class="bi bi-info-circle-fill"></i><span>${message}</span>`;
    document.body.appendChild(toast);
    requestAnimationFrame(() => { toast.style.opacity = '1'; toast.style.transform = 'translateY(0)'; });
    setTimeout(() => { toast.style.opacity = '0'; toast.style.transform = 'translateY(8px)'; setTimeout(() => toast.remove(), 250); }, 3200);
  }
});
