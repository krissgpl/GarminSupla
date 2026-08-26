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

        if (item == :item_1) {

            System.println(
                "Starting WIFI sync test"
            );

            if (Communications has :startSync) {

                Communications.startSync();

            } else {

                System.println(
                    "WIFI sync not supported"
                );
            }

        } else if (item == :item_2) {

            System.println(
                "item 2"
            );
        }
    }
}