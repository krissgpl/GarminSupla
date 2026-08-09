import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaDelegate extends WatchUi.BehaviorDelegate {

    private var _view;
    private var _api;

    function initialize(
        view,
        api
    ) {
        BehaviorDelegate.initialize();

        _view = view;
        _api = api;
    }

    function onMenu() as Boolean {
        WatchUi.pushView(
            new Rez.Menus.MainMenu(),
            new GarminSuplaMenuDelegate(),
            WatchUi.SLIDE_UP
        );

        return true;
    }

	    function onSelect() as Boolean {

        var itemId = _view.getItemId();
        var itemType = _view.getItemType();

        if (itemId == null) {
            System.println(
                "SELECT ignored: no configured item"
            );

            return true;
        }

        System.println(
            "SELECT itemId="
            + itemId
            + " type="
            + itemType
        );

        if (_view.isConfirmationRequired()) {

            var confirmation =
                new WatchUi.Confirmation(
                    "Open / close?"
                );

            WatchUi.pushView(
                confirmation,
                new GarminSuplaConfirmationDelegate(
					_api,
					itemId
				),
                WatchUi.SLIDE_IMMEDIATE
            );

            return true;
        }

        System.println(
            "Confirmation not required"
        );

        return true;
    }

	function onNextPage() as Lang.Boolean {
		System.println("NEXT PAGE");

		_view.selectNextItem();

		return true;
	}

	function onPreviousPage() as Lang.Boolean {
		System.println("PREVIOUS PAGE");

		_view.selectPreviousItem();

		return true;
	}

}
