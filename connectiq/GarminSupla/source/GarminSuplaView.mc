import Toybox.Application;
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
	private var _doubleSwingGateClosedBitmap = null;
	private var _doubleSwingGateOpenedBitmap = null;
	private var _doubleSwingGateUnknownBitmap = null;
	private var _doubleSwingGateOfflineBitmap = null;

	function initialize() {
		View.initialize();

		_statusTimer = new Timer.Timer();

		_doubleSwingGateClosedBitmap =
			Application.loadResource(
				Rez.Drawables.DoubleSwingGateClosed
			);

		_doubleSwingGateOpenedBitmap =
			Application.loadResource(
				Rez.Drawables.DoubleSwingGateOpened
			);

		_doubleSwingGateUnknownBitmap =
			Application.loadResource(
				Rez.Drawables.DoubleSwingGateUnknown
			);

		_doubleSwingGateOfflineBitmap =
			Application.loadResource(
				Rez.Drawables.DoubleSwingGateOffline
			);
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

		if (_itemName != null) {
			_itemConnected = false;
			_itemState = "unknown";
		}

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

		var gateWidth = 88;
		var gateHeight = 38;

		var left =
			centerX - (gateWidth / 2);

		var right =
			centerX + (gateWidth / 2);

		var top =
			centerY - (gateHeight / 2);

		var bottom =
			centerY + (gateHeight / 2);

		var middle = centerX;

		var structureColor =
			_itemConnected
				? Graphics.COLOR_WHITE
				: Graphics.COLOR_DK_GRAY;

		var accentColor =
			_itemConnected
				? Graphics.COLOR_GREEN
				: Graphics.COLOR_DK_GRAY;

		//
		// Subtelne zielone podświetlenie pod bramą
		//
		dc.setColor(
			accentColor,
			Graphics.COLOR_TRANSPARENT
		);

		dc.drawLine(
			left + 4,
			bottom + 6,
			right - 4,
			bottom + 6
		);

		if (_itemConnected) {
			dc.drawLine(
				left + 14,
				bottom + 8,
				right - 14,
				bottom + 8
			);
		}

		//
		// Słupki
		//
		dc.setColor(
			structureColor,
			Graphics.COLOR_TRANSPARENT
		);

		dc.drawRectangle(
			left,
			top - 3,
			7,
			gateHeight + 8
		);

		dc.drawRectangle(
			right - 7,
			top - 3,
			7,
			gateHeight + 8
		);

		//
		// Lampy na słupkach
		//
		dc.setColor(
			accentColor,
			Graphics.COLOR_TRANSPARENT
		);

		dc.fillRectangle(
			left + 1,
			top - 8,
			5,
			4
		);

		dc.fillRectangle(
			right - 6,
			top - 8,
			5,
			4
		);

		dc.setColor(
			structureColor,
			Graphics.COLOR_TRANSPARENT
		);

		//
		// Brama zamknięta
		//
		if (_itemState.equals("closed")) {

			var leafWidth =
				(gateWidth / 2) - 10;

			dc.drawRectangle(
				left + 8,
				top,
				leafWidth,
				gateHeight
			);

			dc.drawRectangle(
				middle + 2,
				top,
				leafWidth,
				gateHeight
			);

			//
			// Pionowe szczeble
			//
			var barX = left + 16;

			while (
				barX < middle - 4
			) {
				dc.drawLine(
					barX,
					top + 3,
					barX,
					bottom - 3
				);

				barX += 9;
			}

			barX = middle + 10;

			while (
				barX < right - 9
			) {
				dc.drawLine(
					barX,
					top + 3,
					barX,
					bottom - 3
				);

				barX += 9;
			}

			return;
		}

		//
		// Brama otwarta
		//
		if (_itemState.equals("opened")) {

			//
			// Lewe skrzydło
			//
			dc.drawLine(
				left + 8,
				top,
				middle - 14,
				centerY - 7
			);

			dc.drawLine(
				left + 8,
				bottom,
				middle - 14,
				centerY + 7
			);

			dc.drawLine(
				middle - 14,
				centerY - 7,
				middle - 14,
				centerY + 7
			);

			//
			// Prawe skrzydło
			//
			dc.drawLine(
				right - 8,
				top,
				middle + 14,
				centerY - 7
			);

			dc.drawLine(
				right - 8,
				bottom,
				middle + 14,
				centerY + 7
			);

			dc.drawLine(
				middle + 14,
				centerY - 7,
				middle + 14,
				centerY + 7
			);

			//
			// Szczeble otwartych skrzydeł
			//
			dc.drawLine(
				left + 16,
				top + 5,
				middle - 14,
				centerY - 3
			);

			dc.drawLine(
				left + 16,
				bottom - 5,
				middle - 14,
				centerY + 3
			);

			dc.drawLine(
				right - 16,
				top + 5,
				middle + 14,
				centerY - 3
			);

			dc.drawLine(
				right - 16,
				bottom - 5,
				middle + 14,
				centerY + 3
			);

			return;
		}

		//
		// UNKNOWN
		//
		dc.setColor(
			Graphics.COLOR_DK_GRAY,
			Graphics.COLOR_TRANSPARENT
		);

		dc.drawLine(
			middle - 10,
			centerY - 10,
			middle + 10,
			centerY + 10
		);

		dc.drawLine(
			middle + 10,
			centerY - 10,
			middle - 10,
			centerY + 10
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

				var gateBitmap = null;

				if (
					!_itemConnected
					&& _doubleSwingGateOfflineBitmap != null
				) {
					gateBitmap =
						_doubleSwingGateOfflineBitmap;

				} else if (
					_itemState.equals("closed")
					&& _doubleSwingGateClosedBitmap != null
				) {
					gateBitmap =
						_doubleSwingGateClosedBitmap;

				} else if (
					_itemState.equals("opened")
					&& _doubleSwingGateOpenedBitmap != null
				) {
					gateBitmap =
						_doubleSwingGateOpenedBitmap;

				} else if (
					_doubleSwingGateUnknownBitmap != null
				) {
					gateBitmap =
						_doubleSwingGateUnknownBitmap;
				}

				if (gateBitmap != null) {

					var bitmapWidth =
						gateBitmap.getWidth();

					var bitmapHeight =
						gateBitmap.getHeight();

					dc.drawBitmap(
						(width - bitmapWidth) / 2,
						(height * 0.76).toNumber()
							- (bitmapHeight / 2),
						gateBitmap
					);
				}
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
