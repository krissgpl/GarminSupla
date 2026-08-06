import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaConfirmationDelegate
    extends WatchUi.ConfirmationDelegate {

    private var _api;
    private var _itemId;

    function initialize(
        api,
        itemId
    ) {
        ConfirmationDelegate.initialize();

        _api = api;
        _itemId = itemId;
    }

    function onResponse(response) as Lang.Boolean {

        if (response == WatchUi.CONFIRM_YES) {

            System.println(
                "CONFIRM YES"
            );

            _api.executeAction(
                _itemId,
                "toggle"
            );

        } else {

            System.println(
                "CONFIRM NO"
            );
        }

        return true;
    }
}
