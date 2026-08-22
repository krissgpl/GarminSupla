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
	private var _slidingGateClosedBitmap = null;
	private var _slidingGateOpenedBitmap = null;
	private var _slidingGateUnknownBitmap = null;
	private var _slidingGateOfflineBitmap = null;

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

		_slidingGateClosedBitmap =
			Application.loadResource(
				Rez.Drawables.SlidingGateClosed
			);

		_slidingGateOpenedBitmap =
			Application.loadResource(
				Rez.Drawables.SlidingGateOpened
			);

		_slidingGateUnknownBitmap =
			Application.loadResource(
				Rez.Drawables.SlidingGateUnknown
			);

		_slidingGateOfflineBitmap =
			Application.loadResource(
				Rez.Drawables.SlidingGateOffline
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

				var slidingGateBitmap = null;

				if (
					!_itemConnected
					&& _slidingGateOfflineBitmap != null
				) {
					slidingGateBitmap =
						_slidingGateOfflineBitmap;

				} else if (
					_itemState.equals("closed")
					&& _slidingGateClosedBitmap != null
				) {
					slidingGateBitmap =
						_slidingGateClosedBitmap;

				} else if (
					_itemState.equals("opened")
					&& _slidingGateOpenedBitmap != null
				) {
					slidingGateBitmap =
						_slidingGateOpenedBitmap;

				} else if (
					_slidingGateUnknownBitmap != null
				) {
					slidingGateBitmap =
						_slidingGateUnknownBitmap;
				}

				if (slidingGateBitmap != null) {

					var bitmapWidth =
						slidingGateBitmap.getWidth();

					var bitmapHeight =
						slidingGateBitmap.getHeight();

					dc.drawBitmap(
						(width - bitmapWidth) / 2,
						(height * 0.76).toNumber()
							- (bitmapHeight / 2),
						slidingGateBitmap
					);
				}
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
