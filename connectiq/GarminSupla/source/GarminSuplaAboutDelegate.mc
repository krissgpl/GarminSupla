import Toybox.Lang;
import Toybox.WatchUi;

class GarminSuplaAboutDelegate
    extends WatchUi.BehaviorDelegate {

    function initialize() {
        BehaviorDelegate.initialize();
    }

    function onBack() as Lang.Boolean {

        WatchUi.popView(
            WatchUi.SLIDE_DOWN
        );

        return true;
    }
}