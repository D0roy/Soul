document.addEventListener("DOMContentLoaded", async () => {
    const updates = document.querySelector("#site-updates");
    const hideButton = document.querySelector("#hide-site-updates");
    const content = document.querySelector("#site-update-content");

    if (!updates || !hideButton || !content) {
        return;
    }

    const updateVersion = "2026-10-02-v1";
    const storageKey = "hidden-site-update";

    const hiddenUpdate = localStorage.getItem(storageKey);

    if (hiddenUpdate === updateVersion) {
        updates.hidden = true;
        return;
    }

    try {
        const response = await fetch("/static/updates/latest.html");

        if (!response.ok) {
            throw new Error(
                `Ошибка загрузки обновления: ${response.status}`
            );
        }

        content.innerHTML = await response.text();
    } catch (error) {
        content.textContent = "Не удалось загрузить обновление.";
        console.error(error);
    }

    hideButton.addEventListener("click", () => {
        localStorage.setItem(storageKey, updateVersion);
        updates.hidden = true;
    });
});