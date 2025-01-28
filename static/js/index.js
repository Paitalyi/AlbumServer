(function() {
	document.addEventListener('DOMContentLoaded', function() {
		// 检测页面是否是从缓存加载
		window.addEventListener("pageshow", function(event) {
			if (event.persisted) {
				location.reload(); // 强制刷新 防止打开gallery页面时 因为缓存的文件夹列表没有更新而失败
				// 经测试 某些设备 浏览器仍会失败
			}
		});
	});
})();