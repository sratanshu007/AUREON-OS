#include <QGuiApplication>
#include <QQmlApplicationEngine>
#include <QQmlContext>
#include <QIcon>
#include "../../core/theme-engine/theme_engine.h"
#include "../../core/window-management/window_manager.h"

int main(int argc, char *argv[]) {
    QGuiApplication app(argc, argv);
    app.setApplicationName("AUREON OS");
    app.setOrganizationName("Aureon Foundation");
    app.setApplicationVersion("1.0.0");

    QQmlApplicationEngine engine;

    aureon::core::ThemeEngine themeEngine;
    aureon::core::WindowManager windowManager;

    engine.rootContext()->setContextProperty("themeEngine", QVariant::fromValue(true));
    engine.rootContext()->setContextProperty("aureonVersion", "1.0.0");

    const QUrl url(QStringLiteral("qrc:/apps/desktop-shell/main.qml"));
    QObject::connect(&engine, &QQmlApplicationEngine::objectCreated,
                     &app, [url](QObject *obj, const QUrl &objUrl) {
        if (!obj && url == objUrl)
            QCoreApplication::exit(-1);
    }, Qt::QueuedConnection);

    engine.load(url);

    return app.exec();
}
