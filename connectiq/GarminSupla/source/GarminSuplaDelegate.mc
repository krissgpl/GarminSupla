import Toybox.Application;
import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaDelegate extends WatchUi.BehaviorDelegate {

    private var _view;
    private var _api;

	private const DRAG_THRESHOLD_PX = 35;
	private const DRAG_DUPLICATE_WINDOW_MS = 300;

	// Wartości DragType z Connect IQ API 3.3.0.
	// Używamy wartości liczbowych, żeby zachować
	// kompatybilność projektu z minApiLevel 3.1.0.
	private const DRAG_TYPE_START_VALUE = 0;
	private const DRAG_TYPE_STOP_VALUE = 2;

	private var _dragStartX = null;
	private var _dragStartY = null;
	private var _lastDragNavigationTime = null;

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

            var confirmationText = null;

            if (itemType != null) {

                if (itemType.equals("gate")) {
                    confirmationText =
                        Application.loadResource(
                            Rez.Strings.ConfirmationOpenClose
                        ).toString();

                } else if (
                    itemType.equals("light")
                    || itemType.equals("switch")
                ) {
                    confirmationText =
                        Application.loadResource(
                            Rez.Strings.ConfirmationTurnOnOff
                        ).toString();

                } else if (itemType.equals("scene")) {
                    confirmationText =
                        Application.loadResource(
                            Rez.Strings.ConfirmationExecuteScene
                        ).toString();
                }
            }

            if (confirmationText == null) {
                System.println(
                    "Confirmation ignored: unsupported item type"
                );

                return true;
            }

            var confirmation =
                new WatchUi.Menu2({
                    :title => confirmationText
                });

            confirmation.addItem(
                new WatchUi.MenuItem(
                    Application.loadResource(
                        Rez.Strings.ConfirmationConfirm
                    ).toString(),
                    null,
                    :confirm,
                    {}
                )
            );

            confirmation.addItem(
                new WatchUi.MenuItem(
                    Application.loadResource(
                        Rez.Strings.ConfirmationCancel
                    ).toString(),
                    null,
                    :cancel,
                    {}
                )
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

	function shouldIgnorePageBehavior() as Lang.Boolean {

		if (_lastDragNavigationTime == null) {
			return false;
		}

		var elapsed =
			System.getTimer()
			- _lastDragNavigationTime;

		_lastDragNavigationTime = null;

		return
			elapsed >= 0
			&& elapsed < DRAG_DUPLICATE_WINDOW_MS;
	}

	function onDrag(dragEvent) as Lang.Boolean {

		// DragEvent istnieje od API 3.3.0.
		// Starsze urządzenia nadal korzystają
		// z onNextPage / onPreviousPage.
		if (
			!(dragEvent has :getType)
			|| !(dragEvent has :getCoordinates)
		) {
			return false;
		}

		var dragType =
			dragEvent.getType();

		var coordinates =
			dragEvent.getCoordinates();

		if (dragType == DRAG_TYPE_START_VALUE) {

			_dragStartX = coordinates[0];
			_dragStartY = coordinates[1];

			return true;
		}

		if (dragType != DRAG_TYPE_STOP_VALUE) {
			return true;
		}

		if (
			_dragStartX == null
			|| _dragStartY == null
		) {
			return true;
		}

		var deltaX =
			coordinates[0] - _dragStartX;

		var deltaY =
			coordinates[1] - _dragStartY;

		_dragStartX = null;
		_dragStartY = null;

		var absX = deltaX;
		var absY = deltaY;

		if (absX < 0) {
			absX = -absX;
		}

		if (absY < 0) {
			absY = -absY;
		}

		// Ignorujemy krótkie ruchy oraz gesty
		// bardziej poziome niż pionowe.
		if (
			absY < DRAG_THRESHOLD_PX
			|| absY <= absX
		) {
			return true;
		}

		_lastDragNavigationTime =
			System.getTimer();

		if (deltaY < 0) {

			System.println(
				"DRAG NEXT PAGE"
			);

			_view.selectNextItem();

		} else {

			System.println(
				"DRAG PREVIOUS PAGE"
			);

			_view.selectPreviousItem();
		}

		return true;
	}

	function onNextPage() as Lang.Boolean {

		if (shouldIgnorePageBehavior()) {

			System.println(
				"NEXT PAGE ignored after drag"
			);

			return true;
		}

		System.println("NEXT PAGE");

		_view.selectNextItem();

		return true;
	}

	function onPreviousPage() as Lang.Boolean {

		if (shouldIgnorePageBehavior()) {

			System.println(
				"PREVIOUS PAGE ignored after drag"
			);

			return true;
		}

		System.println("PREVIOUS PAGE");

		_view.selectPreviousItem();

		return true;
	}

}
