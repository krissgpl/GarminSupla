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
	private var _lightOnBitmap = null;
	private var _lightOffBitmap = null;
	private var _lightUnknownBitmap = null;
	private var _lightOfflineBitmap = null;
	private var _switchOnBitmap = null;
	private var _switchOffBitmap = null;
	private var _switchUnknownBitmap = null;
	private var _switchOfflineBitmap = null;
	private var _rollerShutterOpenedBitmap = null;
	private var _rollerShutterPartialBitmap = null;
	private var _rollerShutterClosedBitmap = null;
	private var _rollerShutterOfflineBitmap = null;
	private var _rollerShutterUnknownBitmap = null;
	private var _awningClosedBitmap = null;
	private var _awningPartiallyOpenedBitmap = null;
	private var _awningOpenedBitmap = null;
	private var _awningOfflineBitmap = null;
	private var _awningUnknownBitmap = null;
	private var _garageGateClosedBitmap = null;
	private var _garageGateOpenedBitmap = null;
	private var _garageGateOfflineBitmap = null;
	private var _garageGateUnknownBitmap = null;

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

		_lightOnBitmap =
			Application.loadResource(
				Rez.Drawables.LightOn
			);

		_lightOffBitmap =
			Application.loadResource(
				Rez.Drawables.LightOff
			);

		_lightUnknownBitmap =
			Application.loadResource(
				Rez.Drawables.LightUnknown
			);

		_lightOfflineBitmap =
			Application.loadResource(
				Rez.Drawables.LightOffline
			);

		_switchOnBitmap =
			Application.loadResource(
				Rez.Drawables.SwitchOn
			);

		_switchOffBitmap =
			Application.loadResource(
				Rez.Drawables.SwitchOff
			);

		_switchUnknownBitmap =
			Application.loadResource(
				Rez.Drawables.SwitchUnknown
			);

		_switchOfflineBitmap =
			Application.loadResource(
				Rez.Drawables.SwitchOffline
			);

		_rollerShutterOpenedBitmap =
			Application.loadResource(
				Rez.Drawables.RollerShutterOpened
			);

		_rollerShutterPartialBitmap =
			Application.loadResource(
				Rez.Drawables.RollerShutterPartial
			);

		_rollerShutterClosedBitmap =
			Application.loadResource(
				Rez.Drawables.RollerShutterClosed
			);

		_rollerShutterOfflineBitmap =
			Application.loadResource(
				Rez.Drawables.RollerShutterOffline
			);

		_rollerShutterUnknownBitmap =
			Application.loadResource(
				Rez.Drawables.RollerShutterUnknown
			);

		_awningClosedBitmap =
			Application.loadResource(
				Rez.Drawables.AwningClosed
			);

		_awningPartiallyOpenedBitmap =
			Application.loadResource(
				Rez.Drawables.AwningPartiallyOpened
			);

		_awningOpenedBitmap =
			Application.loadResource(
				Rez.Drawables.AwningOpened
			);

		_awningOfflineBitmap =
			Application.loadResource(
				Rez.Drawables.AwningOffline
			);

		_awningUnknownBitmap =
			Application.loadResource(
				Rez.Drawables.AwningUnknown
			);

		_garageGateClosedBitmap =
			Application.loadResource(
				Rez.Drawables.GarageGateClosed
			);

		_garageGateOpenedBitmap =
			Application.loadResource(
				Rez.Drawables.GarageGateOpened
			);

		_garageGateOfflineBitmap =
			Application.loadResource(
				Rez.Drawables.GarageGateOffline
			);

		_garageGateUnknownBitmap =
			Application.loadResource(
				Rez.Drawables.GarageGateUnknown
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
				height * 0.44,
				Graphics.FONT_SMALL,
				_itemConnected
					? "Online"
					: "Offline",
				Graphics.TEXT_JUSTIFY_CENTER
			);

			// CLOSED / OPENED / UNKNOWN
			dc.drawText(
				width / 2,
				height * 0.54,
				Graphics.FONT_MEDIUM,
				_itemState.toUpper(),
				Graphics.TEXT_JUSTIFY_CENTER
			);

			if (
				_itemIcon != null
				&& _itemIcon.equals("garage_gate")
			) {

				var garageGateBitmap = null;

				if (
					!_itemConnected
					&& _garageGateOfflineBitmap != null
				) {
					garageGateBitmap =
						_garageGateOfflineBitmap;

				} else if (
					_itemState.equals("closed")
					&& _garageGateClosedBitmap != null
				) {
					garageGateBitmap =
						_garageGateClosedBitmap;

				} else if (
					_itemState.equals("opened")
					&& _garageGateOpenedBitmap != null
				) {
					garageGateBitmap =
						_garageGateOpenedBitmap;

				} else if (
					_garageGateUnknownBitmap != null
				) {
					garageGateBitmap =
						_garageGateUnknownBitmap;
				}

				if (garageGateBitmap != null) {

					var bitmapWidth =
						garageGateBitmap.getWidth();

					var bitmapHeight =
						garageGateBitmap.getHeight();

					dc.drawBitmap(
						(width - bitmapWidth) / 2,
						(height * 0.76).toNumber()
							- (bitmapHeight / 2),
						garageGateBitmap
					);
				}
			}

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

			if (
				_itemType != null
				&& _itemType.equals("light")
			) {

				var lightBitmap = null;

				if (
					!_itemConnected
					&& _lightOfflineBitmap != null
				) {
					lightBitmap =
						_lightOfflineBitmap;

				} else if (
					_itemState.equals("on")
					&& _lightOnBitmap != null
				) {
					lightBitmap =
						_lightOnBitmap;

				} else if (
					_itemState.equals("off")
					&& _lightOffBitmap != null
				) {
					lightBitmap =
						_lightOffBitmap;

				} else if (
					_lightUnknownBitmap != null
				) {
					lightBitmap =
						_lightUnknownBitmap;
				}

				if (lightBitmap != null) {

					var bitmapWidth =
						lightBitmap.getWidth();

					var bitmapHeight =
						lightBitmap.getHeight();

					dc.drawBitmap(
						(width - bitmapWidth) / 2,
						(height * 0.76).toNumber()
							- (bitmapHeight / 2),
						lightBitmap
					);
				}
			}

			if (
				_itemType != null
				&& _itemIcon.equals("switch")
			) {

				var switchBitmap = null;

				if (
					!_itemConnected
					&& _switchOfflineBitmap != null
				) {
					switchBitmap =
						_switchOfflineBitmap;

				} else if (
					_itemState.equals("on")
					&& _switchOnBitmap != null
				) {
					switchBitmap =
						_switchOnBitmap;

				} else if (
					_itemState.equals("off")
					&& _switchOffBitmap != null
				) {
					switchBitmap =
						_switchOffBitmap;

				} else if (
					_switchUnknownBitmap != null
				) {
					switchBitmap =
						_switchUnknownBitmap;
				}

				if (switchBitmap != null) {

					var bitmapWidth =
						switchBitmap.getWidth();

					var bitmapHeight =
						switchBitmap.getHeight();

					dc.drawBitmap(
						(width - bitmapWidth) / 2,
						(height * 0.76).toNumber()
							- (bitmapHeight / 2),
						switchBitmap
					);
				}
			}

			if (
				_itemType != null
				&& _itemIcon.equals("roller_shutter")
			) {

				var rollerShutterBitmap = null;

				if (
					!_itemConnected
					&& _rollerShutterOfflineBitmap != null
				) {
					rollerShutterBitmap =
						_rollerShutterOfflineBitmap;

				} else if (
					_itemState.equals("opened")
					&& _rollerShutterOpenedBitmap != null
				) {
					rollerShutterBitmap =
						_rollerShutterOpenedBitmap;

				} else if (
					_itemState.equals("closed")
					&& _rollerShutterClosedBitmap != null
				) {
					rollerShutterBitmap =
						_rollerShutterClosedBitmap;

				} else if (
					_itemState.equals("unknown")
					&& _rollerShutterUnknownBitmap != null
				) {
					rollerShutterBitmap =
						_rollerShutterUnknownBitmap;

				} else if (
					_rollerShutterPartialBitmap != null
				) {
					rollerShutterBitmap =
						_rollerShutterPartialBitmap;
				}

				if (rollerShutterBitmap != null) {

					var bitmapWidth =
						rollerShutterBitmap.getWidth();

					var bitmapHeight =
						rollerShutterBitmap.getHeight();

					dc.drawBitmap(
						(width - bitmapWidth) / 2,
						(height * 0.76).toNumber()
							- (bitmapHeight / 2),
						rollerShutterBitmap
					);
				}
			}

			if (
				_itemType != null
				&& _itemIcon.equals("awning")
			) {

				var awningBitmap = null;

				if (
					!_itemConnected
					&& _awningOfflineBitmap != null
				) {
					awningBitmap =
						_awningOfflineBitmap;

				} else if (
					_itemState.equals("collapsed")
					&& _awningClosedBitmap != null
				) {
					awningBitmap =
						_awningClosedBitmap;

				} else if (
					_itemState.equals("expanded")
					&& _awningOpenedBitmap != null
				) {
					awningBitmap =
						_awningOpenedBitmap;

				} else if (
					_itemState.equals("unknown")
					&& _awningUnknownBitmap != null
				) {
					awningBitmap =
						_awningUnknownBitmap;

				} else if (
					_awningPartiallyOpenedBitmap != null
				) {
					awningBitmap =
						_awningPartiallyOpenedBitmap;
				}

				if (awningBitmap != null) {

					var bitmapWidth =
						awningBitmap.getWidth();

					var bitmapHeight =
						awningBitmap.getHeight();

					dc.drawBitmap(
						(width - bitmapWidth) / 2,
						(height * 0.76).toNumber()
							- (bitmapHeight / 2),
						awningBitmap
					);
				}
			}

			// 1/2, 2/2...
			dc.drawText(
				width / 2,
				height * 0.85,
				Graphics.FONT_XTINY,
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

	function applyToggleState() as Void {

		if (
			_itemType != null
			&& (
				_itemType.equals("light")
				|| _itemType.equals("switch")
			)
		) {

			if (_itemState.equals("on")) {
				_itemState = "off";
			} else if (_itemState.equals("off")) {
				_itemState = "on";
			}

			WatchUi.requestUpdate();
		}
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
