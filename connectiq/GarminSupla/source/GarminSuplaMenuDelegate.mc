import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaMenuDelegate
    extends WatchUi.MenuInputDelegate {

    private var _api;

    function initialize(api) {
        MenuInputDelegate.initialize();

        _api = api;
    }

    function onMenuItem(
        item as Symbol
    ) as Void {

        if (item == :wifi_refresh) {

            _api.startWifiRefresh();

        } else if (item == :about) {

            System.println(
                "Opening About"
            );

            WatchUi.pushView(
                new GarminSuplaAboutView(),
                new GarminSuplaAboutDelegate(),
                WatchUi.SLIDE_UP
            );
        }
    }
}