import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaRollerShutterMenuDelegate
    extends WatchUi.Menu2InputDelegate {

    private var _api;
    private var _itemId;

    function initialize(
        api,
        itemId
    ) {
        Menu2InputDelegate.initialize();

        _api = api;
        _itemId = itemId;
    }

    function onSelect(
        item as WatchUi.MenuItem
    ) as Void {

        var id = item.getId();

        if (id == :open) {

            System.println(
                "ROLLER SHUTTER OPEN"
            );

            _api.executeAction(
                _itemId,
                "open"
            );

        } else if (id == :close) {

            System.println(
                "ROLLER SHUTTER CLOSE"
            );

            _api.executeAction(
                _itemId,
                "close"
            );

        } else if (id == :stop) {

            System.println(
                "ROLLER SHUTTER STOP"
            );

            _api.executeAction(
                _itemId,
                "stop"
            );
        }

        WatchUi.popView(
            WatchUi.SLIDE_IMMEDIATE
        );
    }
}