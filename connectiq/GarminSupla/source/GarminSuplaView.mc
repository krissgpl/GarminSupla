import Toybox.Graphics;
import Toybox.Lang;
import Toybox.WatchUi;

class GarminSuplaView extends WatchUi.View {

    private var _pairingCode = null;
    private var _status = "Connecting...";
	private var _itemId = null;
	private var _itemType = null;
	private var _itemName = null;
	private var _statusEnabled = false;
	private var _confirmationRequired = true;

    function initialize() {
        View.initialize();
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
				height * 0.50,
				Graphics.FONT_SMALL,
				_statusEnabled
					? "Status available"
					: "Status unavailable",
				Graphics.TEXT_JUSTIFY_CENTER
			);

			dc.drawText(
				width / 2,
				height * 0.65,
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

	function setConfiguredItem(
		itemId,
		itemType,
		itemName,
		statusEnabled,
		confirmationRequired
	) as Void {

		_pairingCode = null;

		_itemId = itemId;
		_itemType = itemType;
		_itemName = itemName;

		_statusEnabled = statusEnabled;
		_confirmationRequired = confirmationRequired;

		_status = "Connected";

		WatchUi.requestUpdate();
	}

	function setNotConfigured() as Void {

		_pairingCode = null;
		_itemId = null;
		_itemType = null;
		_itemName = null;

		_status = "Configure GarminSupla";

		WatchUi.requestUpdate();
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
