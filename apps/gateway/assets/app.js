const header = document.querySelector('[data-header]');
const menuButton = document.querySelector('[data-menu-button]');
const mobileNav = document.querySelector('[data-mobile-nav]');

const updateHeader = () => header.classList.toggle('scrolled', window.scrollY > 28);
updateHeader();
window.addEventListener('scroll', updateHeader, { passive: true });

const setMenu = (open) => {
  menuButton.setAttribute('aria-expanded', String(open));
  menuButton.setAttribute('aria-label', open ? '关闭菜单' : '打开菜单');
  mobileNav.hidden = !open;
  document.body.classList.toggle('menu-open', open);
  header.classList.toggle('scrolled', open || window.scrollY > 28);
};
menuButton.addEventListener('click', () => setMenu(menuButton.getAttribute('aria-expanded') !== 'true'));
mobileNav.querySelectorAll('a').forEach((link) => link.addEventListener('click', () => setMenu(false)));

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 });
document.querySelectorAll('.reveal').forEach((item) => observer.observe(item));

const openDialog = (dialog) => {
  if (dialog && !dialog.open) dialog.showModal();
};
document.querySelectorAll('[data-dialog]').forEach((button) => {
  button.addEventListener('click', () => openDialog(document.getElementById(button.dataset.dialog)));
});
document.querySelectorAll('[data-close-dialog]').forEach((button) => {
  button.addEventListener('click', () => button.closest('dialog').close());
});
document.querySelectorAll('dialog').forEach((dialog) => {
  dialog.addEventListener('click', (event) => {
    if (event.target === dialog) dialog.close();
  });
});
document.querySelectorAll('[data-close-on-click]').forEach((link) => {
  link.addEventListener('click', () => link.closest('dialog').close());
});

const pathContent = {
  relax: ['从两小时的轻徒步开始。', '选择一条交通方便、海拔变化温和的路线，只带必要装备，把注意力交还给身体和自然。'],
  challenge: ['为自己设定一个可完成的小目标。', '从体能评估、基础装备和同行伙伴开始，再逐步增加距离与难度。'],
  family: ['把第一次户外变成共同记忆。', '优先选择安全、可随时返回的自然路线，给孩子留下观察和玩耍的时间。'],
  learn: ['先掌握一项真正有用的技能。', '路线判断、背包整理或基础急救都可以成为起点。学习之后，再去一次真实场景里验证。'],
};
const pathResult = document.querySelector('[data-path-result]');
document.querySelectorAll('[data-path]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-path]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    const [title, copy] = pathContent[button.dataset.path];
    pathResult.innerHTML = `<span>你的下一步</span><strong>${title}</strong><p>${copy}</p>`;
  });
});

const noticeDialog = document.getElementById('notice-dialog');
const showNotice = (title, copy) => {
  noticeDialog.querySelector('[data-notice-title]').textContent = title;
  noticeDialog.querySelector('[data-notice-copy]').textContent = copy;
  openDialog(noticeDialog);
};

document.querySelectorAll('[data-brand]').forEach((button) => {
  button.addEventListener('click', () => {
    showNotice(`${button.dataset.brand} 品牌世界正在整理。`, '品牌故事、产品体系、真实体验和门店服务将在核实后逐步开放。');
  });
});

const storeDialog = document.getElementById('store-dialog');
document.querySelectorAll('[data-store]').forEach((button) => {
  button.addEventListener('click', () => {
    document.querySelectorAll('[data-store]').forEach((item) => item.classList.remove('active'));
    button.classList.add('active');
    storeDialog.querySelector('[data-store-status]').textContent = `已选择：${button.dataset.store}。详细资料核实后开放。`;
    openDialog(storeDialog);
  });
});

document.querySelectorAll('[data-future]').forEach((button) => {
  button.addEventListener('click', () => showNotice(`${button.dataset.future} 正在准备。`, '我们正在连接真实体验、个人成长和长期社群。准备好之后，这里会成为新的入口。'));
});

document.querySelectorAll('[data-reserved-link]').forEach((link) => {
  link.addEventListener('click', (event) => {
    event.preventDefault();
    showNotice(`${link.querySelector('strong').textContent} 正在接入。`, '当前先保留入口，不跳转到未完成页面。');
  });
});
