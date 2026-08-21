import Toybox.Graphics;
import Toybox.Lang;
import Toybox.Timer;
import Toybox.WatchUi;

class GarminSuplaView extends WatchUi.View {

    private var _pairingCode = null;
	private var _serverNotConfigured = false;
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
	private var _itemIcon = "default";

    function initialize() {
        View.initialize();
		_statusTimer = new Timer.Timer();
    }

    function setPairingCode(code) as Void {
		_serverNotConfigured = false;
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

	function setServerNotConfigured() as Void {
		_pairingCode = null;
		_serverNotConfigured = true;
		_status = "Garmin Connect";

		WatchUi.requestUpdate();
	}

    function onLayout(dc as Dc) as Void {
    }

    function onShow() as Void {
    }

	function getItemPositionText() as Lang.String {

		if (_items.size() == 0) {
			return "";
		}

		return
			(_selectedIndex + 1).toString()
			+ "/"
			+ _items.size().toString();
	}

	function drawSlidingGateIcon(
		dc as Dc,
		centerX,
		centerY
	) as Void {

		dc.setColor(
			Graphics.COLOR_WHITE,
			Graphics.COLOR_TRANSPARENT
		);

		var gateWidth = 58;
		var gateHeight = 26;

		var left = centerX - (gateWidth / 2);
		var top = centerY - (gateHeight / 2);
		var bottom = centerY + (gateHeight / 2);

		// Słupki
		dc.drawLine(
			left,
			top - 4,
			left,
			bottom + 4
		);

		dc.drawLine(
			left + gateWidth,
			top - 4,
			left + gateWidth,
			bottom + 4
		);

		// Prowadnica
		dc.drawLine(
			left - 5,
			bottom + 4,
			left + gateWidth + 5,
			bottom + 4
		);

		if (_itemState.equals("closed")) {

			// Skrzydło zamknięte
			dc.drawRectangle(
				left + 4,
				top,
				gateWidth - 8,
				gateHeight
			);

			// Pionowe elementy skrzydła
			dc.drawLine(
				left + 17,
				top,
				left + 17,
				bottom
			);

			dc.drawLine(
				left + 29,
				top,
				left + 29,
				bottom
			);

			dc.drawLine(
				left + 41,
				top,
				left + 41,
				bottom
			);

			return;
		}

		if (_itemState.equals("opened")) {

			// Otwarte światło przejazdu
			// Skrzydło odsunięte w lewo
			dc.drawRectangle(
				left - 16,
				top,
				20,
				gateHeight
			);

			dc.drawLine(
				left - 9,
				top,
				left - 9,
				bottom
			);

			return;
		}

		// UNKNOWN
		dc.drawLine(
			left + 8,
			top + 4,
			left + gateWidth - 8,
			bottom - 4
		);

		dc.drawLine(
			left + gateWidth - 8,
			top + 4,
			left + 8,
			bottom - 4
		);
	}

	function drawDoubleSwingGateIcon(
		dc as Dc,
		centerX,
		centerY
	) as Void {

		dc.setColor(
			Graphics.COLOR_WHITE,
			Graphics.COLOR_TRANSPARENT
		);

		var gateWidth = 58;
		var gateHeight = 26;

		var left = centerX - (gateWidth / 2);
		var right = centerX + (gateWidth / 2);
		var top = centerY - (gateHeight / 2);
		var bottom = centerY + (gateHeight / 2);
		var middle = centerX;

		// Słupki
		dc.drawLine(
			left,
			top - 4,
			left,
			bottom + 4
		);

		dc.drawLine(
			right,
			top - 4,
			right,
			bottom + 4
		);

		if (_itemState.equals("closed")) {

			// Lewe skrzydło
			dc.drawRectangle(
				left + 4,
				top,
				(gateWidth / 2) - 4,
				gateHeight
			);

			// Prawe skrzydło
			dc.drawRectangle(
				middle,
				top,
				(gateWidth / 2) - 4,
				gateHeight
			);

			return;
		}

		if (_itemState.equals("opened")) {

			// Lewe skrzydło otwarte
			dc.drawLine(
				left + 4,
				top,
				middle - 10,
				centerY
			);

			dc.drawLine(
				left + 4,
				bottom,
				middle - 10,
				centerY
			);

			// Prawe skrzydło otwarte
			dc.drawLine(
				right - 4,
				top,
				middle + 10,
				centerY
			);

			dc.drawLine(
				right - 4,
				bottom,
				middle + 10,
				centerY
			);

			return;
		}

		// UNKNOWN
		dc.drawLine(
			left + 8,
			top + 4,
			right - 8,
			bottom - 4
		);

		dc.drawLine(
			right - 8,
			top + 4,
			left + 8,
			bottom - 4
		);
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
			height * 0.12,
			Graphics.FONT_MEDIUM,
			"GarminSupla",
			Graphics.TEXT_JUSTIFY_CENTER
		);

		if (_itemName != null) {

			var arrowX = width / 2;

			// Górny chevron
			var arrowTopY = (height * 0.27).toNumber();

			dc.drawLine(
				arrowX - 8,
				arrowTopY + 6,
				arrowX,
				arrowTopY
			);

			dc.drawLine(
				arrowX,
				arrowTopY,
				arrowX + 8,
				arrowTopY + 6
			);

			// Nazwa itemu
			dc.drawText(
				width / 2,
				height * 0.32,
				Graphics.FONT_SMALL,
				_itemName,
				Graphics.TEXT_JUSTIFY_CENTER
			);

			// Online / Offline
			dc.drawText(
				width / 2,
				height * 0.47,
				Graphics.FONT_SMALL,
				_itemConnected
					? "Online"
					: "Offline",
				Graphics.TEXT_JUSTIFY_CENTER
			);

			// CLOSED / OPENED / UNKNOWN
			dc.drawText(
				width / 2,
				height * 0.57,
				Graphics.FONT_MEDIUM,
				_itemState.toUpper(),
				Graphics.TEXT_JUSTIFY_CENTER
			);

			if (
				_itemIcon != null
				&& _itemIcon.equals("sliding_gate")
			) {
				drawSlidingGateIcon(
					dc,
					width / 2,
					(height * 0.76).toNumber()
				);
			}

			if (
				_itemIcon != null
				&& _itemIcon.equals("double_swing_gate")
			) {
				drawDoubleSwingGateIcon(
					dc,
					width / 2,
					(height * 0.76).toNumber()
				);
			}

			// 1/2, 2/2...
			dc.drawText(
				width / 2,
				height * 0.82,
				Graphics.FONT_SMALL,
				getItemPositionText(),
				Graphics.TEXT_JUSTIFY_CENTER
			);

			// Dolny chevron
			var arrowBottomY = (height * 0.94).toNumber();

			dc.drawLine(
				arrowX - 8,
				arrowBottomY,
				arrowX,
				arrowBottomY + 6
			);

			dc.drawLine(
				arrowX,
				arrowBottomY + 6,
				arrowX + 8,
				arrowBottomY
			);

			return;
		}

		var pairingTitleY =
			(height * 0.26).toNumber();

		dc.drawText(
			width / 2,
			pairingTitleY,
			Graphics.FONT_TINY,
			_serverNotConfigured
				? "Configure server"
				: "Pair your watch",
			Graphics.TEXT_JUSTIFY_CENTER
		);

		if (_pairingCode != null) {

			var codeY =
				pairingTitleY
				+ dc.getFontHeight(
					Graphics.FONT_TINY
				)
				+ 10;

			dc.drawText(
				width / 2,
				codeY,
				Graphics.FONT_MEDIUM,
				_pairingCode,
				Graphics.TEXT_JUSTIFY_CENTER
			);

			var instructionY =
				codeY
				+ dc.getFontHeight(
					Graphics.FONT_MEDIUM
				)
				+ 10;

			dc.drawText(
				width / 2,
				instructionY,
				Graphics.FONT_TINY,
				"Enter this code",
				Graphics.TEXT_JUSTIFY_CENTER
			);

			instructionY +=
				dc.getFontHeight(
					Graphics.FONT_TINY
				);

			dc.drawText(
				width / 2,
				instructionY,
				Graphics.FONT_TINY,
				"in GarminSupla",
				Graphics.TEXT_JUSTIFY_CENTER
			);
		}

		var statusY =
				(height * 0.76).toNumber();

		dc.drawText(
			width / 2,
			statusY,
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

		if (_items.size() == 0) {
			setNotConfigured();
			return;
		}

		if (_selectedIndex >= _items.size()) {
			_selectedIndex = 0;
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

		var itemIcon = item["icon"];

		if (itemIcon != null) {
			_itemIcon = itemIcon.toString();
		} else {
			_itemIcon = "default";
		}

		_status = "Connected";

		System.println(
			"Selected item "
			+ (_selectedIndex + 1)
			+ "/"
			+ _items.size()
			+ ": "
			+ _itemName
			+ " icon="
			+ _itemIcon
		);

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
