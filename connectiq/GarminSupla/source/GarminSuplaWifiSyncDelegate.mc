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

    function initialize() {
        SyncDelegate.initialize();
    }

    function isSyncNeeded() as Lang.Boolean {
        return true;
    }

    function onStartSync() as Void {

        System.println(
            "WIFI SYNC started"
        );

        var serverUrl =
            Application.Properties.getValue(
                "serverUrl"
            );

        if (serverUrl == null) {

            System.println(
                "WIFI SYNC: server URL missing"
            );

            Communications.notifySyncComplete(
                "Server URL missing"
            );

            return;
        }

        var token =
            Application.Storage.getValue(
                "watch_token"
            );

        if (token == null) {

            System.println(
                "WIFI SYNC: watch token missing"
            );

            Communications.notifySyncComplete(
                "Watch token missing"
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

        var url =
            baseUrl
            + "/api/v1/watch/config";

        var options = {
            :method =>
                Communications.HTTP_REQUEST_METHOD_GET,

            :headers => {
                "Authorization" =>
                    "Bearer "
                    + token.toString()
            },

            :responseType =>
                Communications.HTTP_RESPONSE_CONTENT_TYPE_JSON
        };

        System.println(
            "WIFI SYNC GET "
            + url
        );

        Communications.notifySyncProgress(
            0
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
				"Invalid config"
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

        Communications.notifySyncComplete(
            null
        );
    }
}