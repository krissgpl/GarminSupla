import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaMenuDelegate
    extends WatchUi.Menu2InputDelegate {

    private var _api;

    function initialize(api) {
        Menu2InputDelegate.initialize();

        _api = api;
    }

    function onSelect(
        item as WatchUi.MenuItem
    ) as Void {

        var id =
            item.getId();

        if (id == :wifi_refresh) {

            _api.startWifiRefresh();

        } else if (id == :about) {

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