import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaAwningMenuDelegate
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

        if (id == :collapse) {

            System.println(
                "AWNING COLLAPSE"
            );

            _api.executeAction(
                _itemId,
                "collapse"
            );

        } else if (id == :expand) {

            System.println(
                "AWNING EXPAND"
            );

            _api.executeAction(
                _itemId,
                "expand"
            );

        } else if (id == :stop) {

            System.println(
                "AWNING STOP"
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