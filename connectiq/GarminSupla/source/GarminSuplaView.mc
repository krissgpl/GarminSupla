import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Timer;
import Toybox.WatchUi;

class GarminSuplaView extends WatchUi.View {

    private var _pairingCode = null;
    private var _status = "Connecting...";
	private var _itemId = null;
	private var _itemType = null;
	private var _itemName = null;
	private var _statusEnabled = false;
	private var _confirmationRequired = true;
	private var _statusTimer;
	private var _items = [];
	private var _selectedIndex = 0;
	private var _itemConnected = false;
	private var _itemState = "unknown";

    function initialize() {
        View.initialize();
		_statusTimer = new Timer.Timer();
    }

    function setPairingCode(code) as Void {
        _pairingCode = code;
        _status = "Waiting for pairing";

        WatchUi.requestUpdate();
    }

	function setPairingApproved() as Void {
		_status = "Pairing approved";

		WatchUi.requestUpdate();
	}

	function setAuthenticated() as Void {

		_pairingCode = null;
		_status = "Watch connected";

		WatchUi.requestUpdate();
	}

    function setError() as Void {
        _status = "Connection error";

        WatchUi.requestUpdate();
    }

    function onLayout(dc as Dc) as Void {
    }

    function onShow() as Void {
    }

    function onUpdate(dc as Dc) as Void {

        dc.setColor(
            Graphics.COLOR_WHITE,
            Graphics.COLOR_BLACK
        );

        dc.clear();

        var width = dc.getWidth();
        var height = dc.getHeight();

        dc.drawText(
			width / 2,
			height * 0.18,
			Graphics.FONT_MEDIUM,
			"GarminSupla",
			Graphics.TEXT_JUSTIFY_CENTER
		);

		if (_itemName != null) {

			dc.drawText(
				width / 2,
				height * 0.34,
				Graphics.FONT_MEDIUM,
				_itemName,
				Graphics.TEXT_JUSTIFY_CENTER
			);

			dc.drawText(
				width / 2,
				height * 0.48,
				Graphics.FONT_SMALL,
				_itemConnected
					? "Connected"
					: "Offline",
				Graphics.TEXT_JUSTIFY_CENTER
			);

			dc.drawText(
				width / 2,
				height * 0.58,
				Graphics.FONT_MEDIUM,
				_itemState.toUpper(),
				Graphics.TEXT_JUSTIFY_CENTER
			);

			dc.drawText(
				width / 2,
				height * 0.72,
				Graphics.FONT_TINY,
				_status,
				Graphics.TEXT_JUSTIFY_CENTER
			);

			return;
		}

		dc.drawText(
			width / 2,
			height * 0.30,
			Graphics.FONT_SMALL,
			"Pair your watch",
			Graphics.TEXT_JUSTIFY_CENTER
		);

		if (_pairingCode != null) {

			dc.drawText(
				width / 2,
				height * 0.40,
				Graphics.FONT_LARGE,
				_pairingCode,
				Graphics.TEXT_JUSTIFY_CENTER
			);

			dc.drawText(
				width / 2,
				height * 0.55,
				Graphics.FONT_TINY,
				"Enter this code",
				Graphics.TEXT_JUSTIFY_CENTER
			);

			dc.drawText(
				width / 2,
				height * 0.62,
				Graphics.FONT_TINY,
				"in GarminSupla",
				Graphics.TEXT_JUSTIFY_CENTER
			);
		}

		dc.drawText(
			width / 2,
			height * 0.72,
			Graphics.FONT_TINY,
			_status,
			Graphics.TEXT_JUSTIFY_CENTER
		);
    }

    function onHide() as Void {
    }

	function setConfiguredItems(
		items
	) as Void {

		_pairingCode = null;
		_items = items;
		_selectedIndex = 0;

		if (_items.size() == 0) {
			setNotConfigured();
			return;
		}

		System.println(
			"View loaded "
			+ _items.size()
			+ " item(s)"
		);

		selectCurrentItem();
	}

	function selectCurrentItem() as Void {

		if (_items.size() == 0) {
			setNotConfigured();
			return;
		}

		var item = _items[_selectedIndex];

		if (!(item instanceof Lang.Dictionary)) {
			setError();
			return;
		}

		var itemId = item["id"];
		var itemType = item["type"];
		var itemName = item["name"];

		if (
			itemId == null
			|| itemType == null
			|| itemName == null
		) {
			setError();
			return;
		}

		_itemId = itemId.toString();
		_itemType = itemType.toString();
		_itemName = itemName.toString();

		_statusEnabled =
			item["status_enabled"] == true;

		_confirmationRequired =
			item["confirmation_required"] == true;

		_itemConnected =
			item["connected"] == true;

		var itemState = item["state"];

		if (itemState != null) {
			_itemState = itemState.toString();
		} else {
			_itemState = "unknown";
		}

		_status = "Connected";

		WatchUi.requestUpdate();
	}

	function selectNextItem() as Void {

		if (_items.size() <= 1) {
			return;
		}

		_selectedIndex += 1;

		if (_selectedIndex >= _items.size()) {
			_selectedIndex = 0;
		}

		selectCurrentItem();
	}

	function selectPreviousItem() as Void {

		if (_items.size() <= 1) {
			return;
		}

		_selectedIndex -= 1;

		if (_selectedIndex < 0) {
			_selectedIndex = _items.size() - 1;
		}

		selectCurrentItem();
	}

	function setNotConfigured() as Void {

		_pairingCode = null;
		_items = [];

		_itemId = null;
		_itemType = null;
		_itemName = null;

		_status = "Configure GarminSupla";

		WatchUi.requestUpdate();
	}

	function resetActionStatus() as Void {
		_status = "Connected";

		WatchUi.requestUpdate();
	}

	function setActionSending() as Void {
        _status = "Sending...";
        WatchUi.requestUpdate();
    }

    function setActionSuccess() as Void {
        _status = "Action sent";

		WatchUi.requestUpdate();

		_statusTimer.stop();

		_statusTimer.start(
			method(:resetActionStatus),
			2000,
			false
		);
    }

	function getItemId() {
        return _itemId;
    }

    function getItemType() {
        return _itemType;
    }

    function isConfirmationRequired() as Lang.Boolean {
        return _confirmationRequired;
    }

}
