import Toybox.Application;
import Toybox.Lang;
import Toybox.WatchUi;

class GarminSuplaApp extends Application.AppBase {

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {
    }

    function onStop(state as Dictionary?) as Void {
    }

    function getInitialView() as [Views] or [Views, InputDelegates] {

        var view = new GarminSuplaView();

        var api = new GarminSuplaApi(
            view
        );

        api.start();

        return [
            view,
            new GarminSuplaDelegate()
        ];
    }
}

function getApp() as GarminSuplaApp {
    return Application.getApp() as GarminSuplaApp;
}