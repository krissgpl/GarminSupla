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

    private const BASE_URL =
        "https://garmin.krissg.ovh/api/v1";

    private const POLL_INTERVAL_MS = 3000;

    private var _view;
    private var _pairingId = null;
    private var _pollTimer;
    private var _pollInProgress = false;

    function initialize(view) {
        _view = view;
        _pollTimer = new Timer.Timer();
    }

	function start() as Void {

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
			BASE_URL + "/watch/me";

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
			BASE_URL + "/watch/config";

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

		Communications.makeWebRequest(
			url,
			{},
			options,
			method(:onConfigResponse)
		);
	}

	function onConfigResponse(
		responseCode as Lang.Number,
		data as WebResponseData
	) as Void {

		System.println(
			"Watch config HTTP: "
			+ responseCode
		);

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

				return;
			}

			System.println(
				"Watch has no configured items"
			);

			_view.setNotConfigured();

			return;
		}

		if (responseCode == 401) {

			System.println(
				"Watch token rejected while loading config"
			);

			clearCredentials();
			startPairing();

			return;
		}

		System.println(
			"Unable to load watch config"
		);

		_view.setError();
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

		_view.setError();
	}

    function startPairing() as Void {

        var url = BASE_URL + "/watch/pair";

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
            BASE_URL
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
			BASE_URL
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

        var url =
            BASE_URL + "/watch/action";

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

				_view.setActionSuccess();

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
