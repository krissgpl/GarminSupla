import Toybox.Application;
import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaApp extends Application.AppBase {

	private var _api = null;

    function initialize() {
        AppBase.initialize();
    }

    function onStart(state as Dictionary?) as Void {

		var serverUrl =
			Application.Properties.getValue(
				"serverUrl"
			);

		System.println(
			"Configured serverUrl: "
			+ serverUrl
		);
    }

    function onStop(state as Dictionary?) as Void {
    }

	function onSettingsChanged() as Void {

        if (_api == null) {
            return;
        }

        _api.reloadServerUrl();
        _api.start();
    }

    function getInitialView() as [Views] or [Views, InputDelegates] {

        var view = new GarminSuplaView();

        _api = new GarminSuplaApi(
            view
        );

        _api.start();

        return [
            view,
            new GarminSuplaDelegate(
                view,
                _api
            )
        ];
    }
}

function getApp() as GarminSuplaApp {
    return Application.getApp() as GarminSuplaApp;
}
