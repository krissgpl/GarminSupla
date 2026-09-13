import Toybox.Application;
import Toybox.Communications;
import Toybox.Lang;
import Toybox.PersistedContent;
import Toybox.System;

typedef WifiSyncResponseData as
    Null or
    Lang.Dictionary or
    Lang.String or
    PersistedContent.Iterator;

class GarminSuplaWifiSyncDelegate
    extends Communications.SyncDelegate {

    private var _baseUrl = null;
    private var _token = null;

    function initialize() {
        SyncDelegate.initialize();
    }

    function isSyncNeeded() as Lang.Boolean {
        return true;
    }

	function isSupportedAction(
		action as Lang.String
	) as Lang.Boolean {

		return
			action.equals("toggle")
			|| action.equals("open")
			|| action.equals("close")
			|| action.equals("stop")
			|| action.equals("collapse")
			|| action.equals("expand");
	}

    function getSyncErrorText(
        errorCode as Lang.String
    ) as Lang.String {

        var language =
            Application.Storage.getValue(
                "application_language"
            );

        if (language != null) {

            var languageCode =
                language.toString();

            if (languageCode.equals("pl")) {

                if (
                    errorCode.equals(
                        "watch_token_missing"
                    )
                ) {
                    return "Brak tokenu zegarka";
                }

                if (
                    errorCode.equals(
                        "state_missing"
                    )
                ) {
                    return "Brak danych synchronizacji";
                }

                if (
                    errorCode.equals(
                        "action_failed"
                    )
                ) {
                    return "Błąd akcji";
                }

                if (
                    errorCode.equals(
                        "invalid_config"
                    )
                ) {
                    return "Błędna konfiguracja";
                }
            }

            if (languageCode.equals("en")) {

                if (
                    errorCode.equals(
                        "watch_token_missing"
                    )
                ) {
                    return "Watch token missing";
                }

                if (
                    errorCode.equals(
                        "state_missing"
                    )
                ) {
                    return "Sync state missing";
                }

                if (
                    errorCode.equals(
                        "action_failed"
                    )
                ) {
                    return "Action failed";
                }

                if (
                    errorCode.equals(
                        "invalid_config"
                    )
                ) {
                    return "Invalid config";
                }
            }
        }

        if (
            errorCode.equals(
                "watch_token_missing"
            )
        ) {
            return Application.loadResource(
                Rez.Strings.WifiSyncErrorWatchTokenMissing
            ).toString();
        }

        if (
            errorCode.equals(
                "state_missing"
            )
        ) {
            return Application.loadResource(
                Rez.Strings.WifiSyncErrorStateMissing
            ).toString();
        }

        if (
            errorCode.equals(
                "action_failed"
            )
        ) {
            return Application.loadResource(
                Rez.Strings.WifiSyncErrorActionFailed
            ).toString();
        }

        return Application.loadResource(
            Rez.Strings.WifiSyncErrorInvalidConfig
        ).toString();
    }

    function onStartSync() as Void {

        System.println(
            "WIFI SYNC started"
        );

        var serverUrl =
            Application.Properties.getValue(
                "serverUrl"
            );

        var token =
            Application.Storage.getValue(
                "watch_token"
            );

        if (token == null) {

            System.println(
                "WIFI SYNC: watch token missing"
            );

            Communications.notifySyncComplete(
                getSyncErrorText(
                    "watch_token_missing"
                )
			);

            return;
        }

        var baseUrl =
            serverUrl.toString();

        while (
            baseUrl.length() > 0
            && baseUrl.substring(
                baseUrl.length() - 1,
                baseUrl.length()
            ).equals("/")
        ) {
            baseUrl =
                baseUrl.substring(
                    0,
                    baseUrl.length() - 1
                );
        }

        _baseUrl =
            baseUrl + "/api/v1";

        _token =
            token.toString();

        Communications.notifySyncProgress(
            0
        );

        var pendingAction =
            Application.Storage.getValue(
                "wifi_sync_pending_action"
            );

        if (
            pendingAction instanceof Lang.Dictionary
        ) {

            var itemId =
                pendingAction["item_id"];

            var action =
                pendingAction["action"];

			if (
				itemId != null
				&& action != null
				&& isSupportedAction(
					action.toString()
				)
			) {

				System.println(
					"WIFI SYNC pending action found: "
					+ action.toString()
				);

                requestAction(
                    itemId.toString(),
                    action.toString()
                );

                return;
            }

            System.println(
                "WIFI SYNC invalid pending action"
            );

            Application.Storage.deleteValue(
                "wifi_sync_pending_action"
            );
        }

        requestConfig();
    }

    function requestAction(
        itemId as Lang.String,
        action as Lang.String
    ) as Void {

        if (
            _baseUrl == null
            || _token == null
        ) {

            System.println(
                "WIFI SYNC action: missing sync state"
            );

            Application.Storage.deleteValue(
                "wifi_sync_pending_action"
            );

            Communications.notifySyncComplete(
                getSyncErrorText(
                    "state_missing"
                )
			);

            return;
        }

        var url =
            _baseUrl.toString()
            + "/watch/action";

        var params = {
            "item_id" => itemId,
            "action" => action
        };

        var options = {
            :method =>
                Communications.HTTP_REQUEST_METHOD_POST,

            :headers => {
                "Authorization" =>
                    "Bearer "
                    + _token.toString(),

                "Content-Type" =>
                    Communications.REQUEST_CONTENT_TYPE_JSON
            },

            :responseType =>
                Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };

        System.println(
            "WIFI SYNC POST "
            + url
        );

        Communications.makeWebRequest(
            url,
            params,
            options,
            method(:onActionResponse)
        );
    }

    function onActionResponse(
        responseCode as Lang.Number,
        data as WifiSyncResponseData
    ) as Void {

        System.println(
            "WIFI SYNC action HTTP: "
            + responseCode
        );

        if (
            responseCode == 200
            && data instanceof Lang.Dictionary
            && data["success"] == true
        ) {

            System.println(
                "WIFI SYNC action OK"
            );

			// Usuwamy akcję przed odświeżeniem configu,
			// żeby nigdy nie wykonać jej drugi raz,
			// jeśli późniejszy GET config się nie powiedzie.
            Application.Storage.deleteValue(
                "wifi_sync_pending_action"
            );

            Communications.notifySyncProgress(
                50
            );

            requestConfig();

            return;
        }

        System.println(
            "WIFI SYNC action failed"
        );

        Application.Storage.deleteValue(
            "wifi_sync_pending_action"
        );

       Communications.notifySyncComplete(
            getSyncErrorText(
                "action_failed"
            )
		);
    }

    function requestConfig() as Void {

        if (
            _baseUrl == null
            || _token == null
        ) {

            System.println(
                "WIFI SYNC config: missing sync state"
            );

            Communications.notifySyncComplete(
                getSyncErrorText(
                    "state_missing"
                )
			);

            return;
        }

        var url =
            _baseUrl.toString()
            + "/watch/config";

        var options = {
            :method =>
                Communications.HTTP_REQUEST_METHOD_GET,

            :headers => {
                "Authorization" =>
                    "Bearer "
                    + _token.toString()
            },

            :responseType =>
                Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };

        System.println(
            "WIFI SYNC GET "
            + url
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
        data as WifiSyncResponseData
    ) as Void {

        System.println(
            "WIFI SYNC HTTP: "
            + responseCode
        );

        if (
            responseCode == 200
            && data instanceof Lang.Dictionary
        ) {

            System.println(
                "WIFI SYNC config OK"
            );

            Application.Storage.setValue(
                "wifi_sync_config",
                data
            );

            System.println(
                "WIFI SYNC config stored"
            );

            Communications.notifySyncProgress(
                100
            );

            Communications.notifySyncComplete(
                null
            );

            return;
        }

        if (responseCode == 200) {

            System.println(
                "WIFI SYNC invalid config payload"
            );

            Communications.notifySyncComplete(
                getSyncErrorText(
                    "invalid_config"
                )
			);

            return;
        }

        System.println(
            "WIFI SYNC config failed"
        );

        Communications.notifySyncComplete(
            "HTTP "
            + responseCode
        );
    }

    function onStopSync() as Void {

        System.println(
            "WIFI SYNC stopped"
        );

        Communications.cancelAllRequests();

        Application.Storage.deleteValue(
            "wifi_sync_pending_action"
        );

        Communications.notifySyncComplete(
            null
        );
    }
}