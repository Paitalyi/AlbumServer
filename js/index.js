// 检测页面是否是从缓存加载
window.addEventListener("pageshow", function(event) {
	if (event.persisted) {
		location.reload(); // 强制刷新
	}
});