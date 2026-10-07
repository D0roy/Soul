self.addEventListener("push", (event) => {
    let data = {};

    if (event.data) {
        try {
            data = event.data.json();
        } catch (error) {
            data = {
                title: "Soul",
                body: event.data.text(),
            };
        }
    }

    const title = data.title || "Soul";
    const options = {
        body: data.body || "У вас новое уведомление.",
        icon: data.icon || "/static/images/icon_192_for_phone.png",
        badge: data.badge || "/static/images/icon_192_for_phone.png",
        data: {
            url: data.url || "/accounts/notifications/",
        },
    };

    event.waitUntil(
        self.registration.showNotification(title, options)
    );
});


self.addEventListener("notificationclick", (event) => {
    event.notification.close();

    const targetUrl =
        event.notification.data?.url ||
        "/accounts/notifications/";

    event.waitUntil(
        clients.matchAll({
            type: "window",
            includeUncontrolled: true,
        }).then((clientList) => {
            for (const client of clientList) {
                if ("focus" in client) {
                    client.navigate(targetUrl);
                    return client.focus();
                }
            }

            if (clients.openWindow) {
                return clients.openWindow(targetUrl);
            }

            return undefined;
        })
    );
});