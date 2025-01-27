(function () {
    document.addEventListener("DOMContentLoaded", function () {
        const deleteButtons = document.querySelectorAll(".delete-btn");
        const deleteModal = document.getElementById("delete-modal");
        const deleteMsg = document.getElementById("delete-msg");
        const confirmDelete = document.getElementById("confirm-delete");
        const cancelDelete = document.getElementById("cancel-delete");

        deleteButtons.forEach(button => {
            button.addEventListener("click", function () {
                const path = this.getAttribute("data-path");
                deleteMsg.textContent = `你确定要删除文件夹 ${decodeURIComponent(path)} 吗?`;
                confirmDelete.setAttribute("href", `/remove_dir?path=${path}`);
                deleteModal.style.display = "block";
            });
        });

        cancelDelete.addEventListener("click", function () {
            deleteModal.style.display = "none";
        });

        // 点击模态框外部时关闭提示框
        window.addEventListener("click", function (event) {
            if (event.target === deleteModal) {
                deleteModal.style.display = "none";
            }
        });
    });
})();
