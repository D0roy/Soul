function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat(
        (4 - (base64String.length % 4)) % 4
    );

    const base64 = (
        base64String + padding
    )
        .replace(/-/g, "+")
        .replace(/_/g, "/");

    const rawData = window.atob(base64);

    return Uint8Array.from(
        [...rawData].map((char) => char.charCodeAt(0))
    );
}


function getCookie(name) {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const [key, value] = cookie.trim().split("=");

        if (key === name) {
            return decodeURIComponent(value);
        }
    }

    return null;
}


async function enablePushNotifications() {
    if (!("serviceWorker" in navigator)) {
        throw new Error(
            "Браузер не поддерживает Service Worker."
        );
    }

    if (!("PushManager" in window)) {
        throw new Error(
            "Браузер не поддерживает Push API."
        );
    }

    const permission =
        await Notification.requestPermission();

    if (permission !== "granted") {
        throw new Error(
            "Разрешение на уведомления не предоставлено."
        );
    }

    const registration =
        await navigator.serviceWorker.register(
            "/accounts/service-worker.js"
        );

    await navigator.serviceWorker.ready;

    let subscription =
        await registration.pushManager.getSubscription();

    if (!subscription) {
        const publicKey =
            window.PUSH_PUBLIC_KEY;

        if (!publicKey) {
            throw new Error(
                "Не задан VAPID public key."
            );
        }

        subscription =
            await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey:
                    urlBase64ToUint8Array(publicKey),
            });
    }

    const response = await fetch(
        "/accounts/push/subscribe/",
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            credentials: "same-origin",
            body: JSON.stringify(
                subscription.toJSON()
            ),
        }
    );

    if (!response.ok) {
        throw new Error(
            "Сервер не сохранил push-подписку."
        );
    }

    return response.json();
}


async function disablePushNotifications() {
    const response = await fetch(
        "/accounts/push/disable/",
        {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
            },
            credentials: "same-origin",
        }
    );

    if (!response.ok) {
        throw new Error(
            "Сервер не отключил push-подписку."
        );
    }

    return response.json();
}