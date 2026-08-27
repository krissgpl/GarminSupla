import Toybox.Communications;
import Toybox.Lang;
import Toybox.System;
import Toybox.WatchUi;

class GarminSuplaMenuDelegate
    extends WatchUi.MenuInputDelegate {

    function initialize() {
        MenuInputDelegate.initialize();
    }

    function onMenuItem(
        item as Symbol
    ) as Void {

        if (item == :wifi_refresh) {

            System.println(
                "Starting WIFI refresh"
            );

            if (Communications has :startSync) {

                Communications.startSync();

            } else {

                System.println(
                    "WIFI sync not supported"
                );
            }

        } else if (item == :about) {

            System.println(
                "Opening About"
            );

            WatchUi.pushView(
                new GarminSuplaAboutView(),
                new GarminSuplaAboutDelegate(),
                WatchUi.SLIDE_UP
            );
        }
    }
}