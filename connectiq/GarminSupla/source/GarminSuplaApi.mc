import Toybox.Application;
import Toybox.Communications;
import Toybox.Lang;
import Toybox.PersistedContent;
import Toybox.System;
import Toybox.Timer;

typedef WebResponseData as
    Null or
    Lang.Dictionary or
    Lang.String or
    PersistedContent.Iterator;

class GarminSuplaApi {

    private const POLL_INTERVAL_MS = 3000;
	private const CONFIG_REFRESH_INTERVAL_MS = 5000;

	private var _baseUrl;
    private var _view;
    private var _pairingId = null;
    private var _pollTimer;
    private var _pollInProgress = false;

	private var _configTimer;
	private var _configInProgress = false;
	private var _ignoreNextConfigResponse = false;

	function reloadServerUrl() as Void {

		var serverUrl =
			Application.Properties.getValue(
				"serverUrl"
			);

		if (serverUrl == null) {
			_baseUrl = null;
			return;
		}

		var value =
			serverUrl.toString();

		while (
			value.length() > 0
			&& value.substring(
				value.length() - 1,
				value.length()
			).equals("/")
		) {
			value =
				value.substring(
					0,
					value.length() - 1
				);
		}

		if (value.length() == 0) {
			_baseUrl = null;
		} else {
			_baseUrl =
				value + "/api/v1";
		}
	}

    function initialize(view) {
        _view = view;

		reloadServerUrl();

        _pollTimer = new Timer.Timer();
		_configTimer = new Timer.Timer();
    }

	function start() as Void {

		if (_baseUrl == null) {
			System.println(
				"GarminSupla server URL not configured"
			);

			_view.setServerNotConfigured();

			return;
		}

		var token =
			Application.Storage.getValue(
				"watch_token"
			);

		if (token == null) {

			System.println(
				"No stored watch token"
			);

			startPairing();
			return;
		}

		System.println(
			"Stored watch token found"
		);

		verifyWatch(
			token.toString()
		);
	}

	function verifyWatch(token as Lang.String) as Void {

		var url =
			_baseUrl + "/watch/me";

		var options = {
			:method =>
				Communications.HTTP_REQUEST_METHOD_GET,

			:headers => {
				"Authorization" =>
					"Bearer " + token
			},

			:responseType =>
				Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
		};

		System.println(
			"GET " + url
		);

		Communications.makeWebRequest(
			url,
			{},
			options,
			method(:onVerifyWatchResponse)
		);
	}

	function loadConfig() as Void {

		 if (_configInProgress) {
			return;
		}

		var token =
			Application.Storage.getValue(
				"watch_token"
			);

		if (token == null) {
			clearCredentials();
			startPairing();
			return;
		}

		var url =
			_baseUrl + "/watch/config";

		var options = {
			:method =>
				Communications.HTTP_REQUEST_METHOD_GET,

			:headers => {
				"Authorization" =>
					"Bearer " + token.toString()
			},

			:responseType =>
				Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
		};

		System.println(
			"GET " + url
		);

		_configInProgress = true;

		Communications.makeWebRequest(
			url,
			{},
			options,
			method(:onConfigResponse)
		);
	}

	function scheduleNextConfigRefresh() as Void {

		_configTimer.stop();

		_configTimer.start(
			method(:refreshConfig),
			CONFIG_REFRESH_INTERVAL_MS,
			false
		);
	}

	function refreshConfig() as Void {

		if (_configInProgress) {
			scheduleNextConfigRefresh();
			return;
		}

		loadConfig();
	}

	function stopConfigPolling() as Void {

		_configTimer.stop();
		_configInProgress = false;
	}

	function onConfigResponse(
		responseCode as Lang.Number,
		data as WebResponseData
	) as Void {

		System.println(
			"Watch config HTTP: "
			+ responseCode
		);

		_configInProgress = false;

		if (_ignoreNextConfigResponse) {

			_ignoreNextConfigResponse = false;

			System.println(
				"Ignoring stale watch config response after action"
			);

			scheduleNextConfigRefresh();

			return;
		}

		if (
			responseCode == 200
			&& data instanceof Lang.Dictionary
		) {

			var configured =
				data["configured"];

			var items =
				data["items"];

			if (
				configured == true
				&& items instanceof Lang.Array
				&& items.size() > 0
			) {

				System.println(
					"Watch config loaded: "
					+ items.size()
					+ " item(s)"
				);

				System.println(
					"Watch config first item: "
					+ items[0]
				);

				_view.setConfiguredItems(
					items
				);

				scheduleNextConfigRefresh();

				return;
			}

			System.println(
				"Watch has no configured items"
			);

			_view.setNotConfigured();

			scheduleNextConfigRefresh();

			return;
		}

		if (responseCode == 401) {

			System.println(
				"Watch token rejected while loading config"
			);

			stopConfigPolling();

			clearCredentials();
			startPairing();

			return;
		}

		System.println(
			"Unable to load watch config"
		);

		if (loadStoredWifiConfig()) {

			System.println(
				"Watch config restored from WIFI snapshot"
			);

			scheduleNextConfigRefresh();

			return;
		}

		_view.setError();

		scheduleNextConfigRefresh();
	}

	function clearCredentials() as Void {

		Application.Storage.deleteValue(
			"watch_id"
		);

		Application.Storage.deleteValue(
			"watch_token"
		);

		System.println(
			"Stored watch credentials cleared"
		);
	}

	function loadStoredWifiConfig() as Lang.Boolean {

		var storedConfig =
			Application.Storage.getValue(
				"wifi_sync_config"
			);

		if (!(storedConfig instanceof Lang.Dictionary)) {

			System.println(
				"No stored WIFI sync config"
			);

			return false;
		}

		var configured =
			storedConfig["configured"];

		var items =
			storedConfig["items"];

		if (
			configured != true
			|| !(items instanceof Lang.Array)
			|| items.size() == 0
		) {

			System.println(
				"Stored WIFI sync config invalid"
			);

			return false;
		}

		System.println(
			"Using stored WIFI sync config: "
			+ items.size()
			+ " item(s)"
		);

		_view.setStoredWifiItems(
			items
		);

		return true;
	}

	function scheduleVerifyRetry() as Void {

		_configTimer.stop();

		_configTimer.start(
			method(:retryVerifyWatch),
			CONFIG_REFRESH_INTERVAL_MS,
			false
		);
	}

	function retryVerifyWatch() as Void {

		var token =
			Application.Storage.getValue(
				"watch_token"
			);

		if (token == null) {
			startPairing();
			return;
		}

		verifyWatch(
			token.toString()
		);
	}

	function onVerifyWatchResponse(
		responseCode as Lang.Number,
		data as WebResponseData
	) as Void {

		System.println(
			"Watch verification HTTP: "
			+ responseCode
		);

		if (responseCode == 200) {

			System.println(
				"Stored watch credentials valid"
			);

			loadConfig();

			return;
		}

		if (responseCode == 401) {

			System.println(
				"Stored watch credentials invalid"
			);

			clearCredentials();

			startPairing();

			return;
		}

		System.println(
			"Watch verification failed"
		);

		if (loadStoredWifiConfig()) {

			System.println(
				"Watch view restored from WIFI snapshot"
			);

			scheduleVerifyRetry();

			return;
		}

		_view.setError();

		scheduleVerifyRetry();

	}

    function startPairing() as Void {

		stopConfigPolling();

        var url = _baseUrl + "/watch/pair";

        var options = {
            :method =>
                Communications.HTTP_REQUEST_METHOD_POST,

            :headers => {
                "Content-Type" =>
                    Communications.REQUEST_CONTENT_TYPE_JSON
            },

            :responseType =>
                Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };

        System.println(
            "POST " + url
        );

        Communications.makeWebRequest(
            url,
            {},
            options,
            method(:onPairingResponse)
        );
    }

	function onPairingResponse(
        responseCode as Lang.Number,
        data as WebResponseData
    ) as Void {

        System.println(
            "Pairing HTTP status: "
            + responseCode
        );

        System.println(
            "Pairing response: "
            + data
        );

        if (
            responseCode == 200
            && data instanceof Lang.Dictionary
        ) {

            var code = data["code"];
            var pairingId = data["pairing_id"];

            if (
                code != null
                && pairingId != null
            ) {

                _pairingId =
                    pairingId.toString();

                _view.setPairingCode(
                    code.toString()
                );

                startPolling();

                return;
            }
        }

        _view.setError();
    }

	function scheduleNextPoll() as Void {

		_pollTimer.stop();

		_pollTimer.start(
			method(:pollPairing),
			POLL_INTERVAL_MS,
			false
		);
	}

    function startPolling() as Void {

        if (_pairingId == null) {
            return;
        }

        System.println(
            "Starting pairing polling"
        );

        scheduleNextPoll();
    }

    function stopPolling() as Void {

        _pollTimer.stop();
        _pollInProgress = false;

        System.println(
            "Pairing polling stopped"
        );
    }

    function pollPairing() as Void {

        if (
            _pairingId == null
            || _pollInProgress
        ) {
            return;
        }

        _pollInProgress = true;

        var url =
            _baseUrl
            + "/watch/pair/"
            + _pairingId;

        var options = {
            :method =>
                Communications.HTTP_REQUEST_METHOD_GET,

            :responseType =>
                Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };

        System.println(
            "GET " + url
        );

        Communications.makeWebRequest(
            url,
            {},
            options,
            method(:onPairingStatusResponse)
        );
    }

	function consumePairing() as Void {

		if (_pairingId == null) {
			_view.setError();
			return;
		}

		var url =
			_baseUrl
			+ "/watch/pair/"
			+ _pairingId
			+ "/consume";

		var options = {
			:method =>
				Communications.HTTP_REQUEST_METHOD_POST,

			:headers => {
				"Content-Type" =>
					Communications.REQUEST_CONTENT_TYPE_JSON
			},

			:responseType =>
				Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
		};

		System.println(
			"POST " + url
		);

		Communications.makeWebRequest(
			url,
			{},
			options,
			method(:onConsumeResponse)
		);
	}

	function onConsumeResponse(
		responseCode as Lang.Number,
		data as WebResponseData
	) as Void {

		System.println(
			"Consume HTTP status: "
			+ responseCode
		);

		System.println(
			"Consume response: "
			+ data
		);

		if (
			responseCode == 200
			&& data instanceof Lang.Dictionary
		) {

			var watchId =
				data["watch_id"];

			var token =
				data["token"];

			if (
				watchId != null
				&& token != null
			) {

				Application.Storage.setValue(
					"watch_id",
					watchId.toString()
				);

				Application.Storage.setValue(
					"watch_token",
					token.toString()
				);

				System.println(
					"Watch credentials saved"
				);

				_pairingId = null;

				_view.setAuthenticated();

				loadConfig();

				return;
			}
		}

		System.println(
			"Invalid consume response"
		);

		_view.setError();
	}

	function onPairingStatusResponse(
		responseCode as Lang.Number,
		data as WebResponseData
	) as Void {

		_pollInProgress = false;

		System.println(
			"Pairing status HTTP: "
			+ responseCode
		);

		System.println(
			"Pairing status response: "
			+ data
		);

		if (
			responseCode == 200
			&& data instanceof Lang.Dictionary
		) {

			var pairingStatus =
				data["status"];

			if (pairingStatus != null) {

				var statusText =
					pairingStatus.toString();

				System.println(
					"Pairing status: "
					+ statusText
				);

				if (statusText.equals("pending")) {

					System.println(
						"Pairing still pending"
					);

					scheduleNextPoll();
					return;
				}

				if (statusText.equals("approved")) {

					System.println(
						"Pairing approved"
					);

					stopPolling();

					_view.setPairingApproved();

					consumePairing();

					return;
				}
			}
		}

		System.println(
			"Invalid pairing status response"
		);

		stopPolling();
		_view.setError();
	}

	function executeAction(
        itemId as Lang.String,
        action as Lang.String
    ) as Void {

        var token =
            Application.Storage.getValue(
                "watch_token"
            );

        if (token == null) {
            System.println(
                "Cannot execute action: no watch token"
            );

            _view.setError();
            return;
        }

		if (_view.isUsingStoredWifiConfig()) {

			System.println(
				"Executing action through WIFI sync: "
				+ action
			);

			if (!(Communications has :startSync)) {

				System.println(
					"WIFI sync not supported"
				);

				_view.setError();

				return;
			}

			Application.Storage.setValue(
				"wifi_sync_pending_action",
				{
					"item_id" => itemId,
					"action" => action
				}
			);

			System.println(
				"WIFI sync pending action stored"
			);

			Communications.startSync();

			return;
		}

        var url =
            _baseUrl + "/watch/action";

        var params = {
            "item_id" => itemId,
            "action" => action
        };

        var options = {
            :method =>
                Communications.HTTP_REQUEST_METHOD_POST,

            :headers => {
                "Authorization" =>
                    "Bearer " + token.toString(),

                "Content-Type" =>
                    Communications.REQUEST_CONTENT_TYPE_JSON
            },

            :responseType =>
                Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };

        System.println(
            "POST " + url
        );

		_view.setActionSending();

		if (_configInProgress) {
			System.println(
				"Config request in progress during action; "
				+ "next config response will be ignored"
			);

			_ignoreNextConfigResponse = true;
		}

        Communications.makeWebRequest(
            url,
            params,
            options,
            method(:onActionResponse)
        );
    }

    function onActionResponse(
        responseCode as Lang.Number,
        data as WebResponseData
    ) as Void {

        System.println(
            "Watch action HTTP: "
            + responseCode
        );

        System.println(
            "Watch action response: "
            + data
        );

        if (
            responseCode == 200
            && data instanceof Lang.Dictionary
        ) {
            var success = data["success"];

            if (success == true) {
                System.println(
                    "Watch action succeeded"
                );

				var itemType =
					_view.getItemType();

				_view.applyToggleState();

				_view.setActionSuccess();

				if (
					itemType != null
					&& (
						itemType.equals("light")
						|| itemType.equals("switch")
					)
				) {
					scheduleNextConfigRefresh();
				} else {
					loadConfig();
				}

				return;

            }
        }

        if (responseCode == 401) {
            System.println(
                "Watch token rejected while executing action"
            );

            clearCredentials();
            startPairing();

            return;
        }

        System.println(
            "Watch action failed"
        );

        _view.setError();
    }

}
