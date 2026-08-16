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

		if (
			itemType != null
			&& itemType.equals("roller_shutter")
		) {

			var menu =
				new WatchUi.Menu2({
					:title => "Roller shutter"
				});

			menu.addItem(
				new WatchUi.MenuItem(
					"Open",
					null,
					:open,
					{}
				)
			);

			menu.addItem(
				new WatchUi.MenuItem(
					"Close",
					null,
					:close,
					{}
				)
			);

			menu.addItem(
				new WatchUi.MenuItem(
					"Stop",
					null,
					:stop,
					{}
				)
			);

			WatchUi.pushView(
				menu,
				new GarminSuplaRollerShutterMenuDelegate(
					_api,
					itemId
				),
				WatchUi.SLIDE_IMMEDIATE
			);

			return true;
		}

		if (
			itemType != null
			&& itemType.equals("awning")
		) {

			var menu =
				new WatchUi.Menu2({
					:title => "Awning"
				});

			menu.addItem(
				new WatchUi.MenuItem(
					"Collapse",
					null,
					:collapse,
					{}
				)
			);

			menu.addItem(
				new WatchUi.MenuItem(
					"Expand",
					null,
					:expand,
					{}
				)
			);

			menu.addItem(
				new WatchUi.MenuItem(
					"Stop",
					null,
					:stop,
					{}
				)
			);

			WatchUi.pushView(
				menu,
				new GarminSuplaAwningMenuDelegate(
					_api,
					itemId
				),
				WatchUi.SLIDE_IMMEDIATE
			);

			return true;
		}

		if (_view.isConfirmationRequired()) {

			var confirmationText =
				"Execute action?";

			if (itemType != null) {

				if (itemType.equals("gate")) {
					confirmationText =
						"Open / close?";
				} else if (
					itemType.equals("light")
					|| itemType.equals("switch")
				) {
					confirmationText =
						"Turn on / off?";
				} else if (itemType.equals("scene")) {
					confirmationText =
						"Execute scene?";
				}
			}

			var confirmation =
				new WatchUi.Confirmation(
					confirmationText
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

		_api.executeAction(
			itemId,
			"toggle"
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
