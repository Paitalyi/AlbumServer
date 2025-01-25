(function() {
	document.addEventListener('DOMContentLoaded', function() {
		const navDrop = document.querySelector('.nav-drop');
		const sidebarTrigger = document.querySelector('.sidebar-trigger');

		// // 检测页面是否是从缓存加载
		// window.addEventListener("pageshow", function(event) {
		// 	if (event.persisted) {
		// 		location.reload(); // 强制刷新 防止打开gallery页面时 因为缓存的文件夹列表没有更新而失败
		// 		// 经测试 某些设备 浏览器仍会失败
		// 	}
		// });

		document.querySelector('.sidebar-trigger').addEventListener('click', function(event) {
			event.stopPropagation(); // 阻止事件冒泡，以免触发 document 上的点击事件

			navDrop.classList.toggle('active');
		});

		// 点击页面其他地方时收起 .nav-drop
		document.addEventListener('click', function(event) {
			// 如果点击的不是 sidebar-trigger 和 nav-drop 元素本身，则收起 nav-drop
			if (!sidebarTrigger.contains(event.target) && !navDrop.contains(event.target)) {
				navDrop.classList.remove('active');
			}
		});
	});
})();