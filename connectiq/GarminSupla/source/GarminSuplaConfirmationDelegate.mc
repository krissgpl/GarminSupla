import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaConfirmationDelegate
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

        if (id == :confirm) {

            System.println(
                "CONFIRM YES"
            );

            _api.executeAction(
                _itemId,
                "toggle"
            );

        } else if (id == :cancel) {

            System.println(
                "CONFIRM NO"
            );
        }

        WatchUi.popView(
            WatchUi.SLIDE_IMMEDIATE
        );
    }
}