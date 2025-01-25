(function() {
	document.addEventListener('DOMContentLoaded', function() {
		const toggle = document.getElementById('night-mode-toggle');
		const icon = document.getElementById('night-mode-icon');
		// 初始化检查
		if (localStorage.getItem('darkModeEnabled') === 'true') {
			document.body.classList.add('dark-mode');
			icon.src = '/static/asset/moon.svg';
		}
		// 切换黑暗模式
		toggle.addEventListener('click', function() {
			const isDarkMode = document.body.classList.toggle('dark-mode');
			localStorage.setItem('darkModeEnabled', isDarkMode);
			// 更新图标
			if (isDarkMode) {
				icon.src = '/static/asset/moon.svg';
			} else {
				icon.src = '/static/asset/sun.svg';
			}
		});
	});
})();