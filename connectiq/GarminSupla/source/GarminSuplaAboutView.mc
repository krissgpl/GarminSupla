import Toybox.Application;
import Toybox.Graphics;
import Toybox.WatchUi;

class GarminSuplaAboutView
    extends WatchUi.View {

    private var _appName;
    private var _versionLabel;
    private var _version;
    private var _authorLabel;
    private var _author;
    private var _emailLabel;
    private var _email;

    function initialize() {
        View.initialize();

        _appName =
            Application.loadResource(
                Rez.Strings.AppName
            );

        _versionLabel =
            Application.loadResource(
                Rez.Strings.AboutVersionLabel
            );

        _version =
            Application.loadResource(
                Rez.Strings.AboutVersion
            );

        _authorLabel =
            Application.loadResource(
                Rez.Strings.AboutAuthorLabel
            );

        _author =
            Application.loadResource(
                Rez.Strings.AboutAuthor
            );

        _emailLabel =
            Application.loadResource(
                Rez.Strings.AboutEmailLabel
            );

        _email =
            Application.loadResource(
                Rez.Strings.AboutEmail
            );
    }

    function onLayout(dc as Graphics.Dc) as Void {
    }

    function onShow() as Void {
    }

	function onUpdate(dc as Graphics.Dc) as Void {

		dc.setColor(
			Graphics.COLOR_WHITE,
			Graphics.COLOR_BLACK
		);

		dc.clear();

		var width = dc.getWidth();
		var height = dc.getHeight();

		// Application name
		dc.drawText(
			width / 2,
			height * 0.10,
			Graphics.FONT_MEDIUM,
			_appName,
			Graphics.TEXT_JUSTIFY_CENTER
		);

		// Author
		dc.drawText(
			width / 2,
			height * 0.31,
			Graphics.FONT_XTINY,
			_authorLabel,
			Graphics.TEXT_JUSTIFY_CENTER
		);

		dc.drawText(
			width / 2,
			height * 0.39,
			Graphics.FONT_SMALL,
			_author,
			Graphics.TEXT_JUSTIFY_CENTER
		);

		// E-mail
		dc.drawText(
			width / 2,
			height * 0.53,
			Graphics.FONT_XTINY,
			_emailLabel,
			Graphics.TEXT_JUSTIFY_CENTER
		);

		dc.drawText(
			width / 2,
			height * 0.61,
			Graphics.FONT_XTINY,
			_email,
			Graphics.TEXT_JUSTIFY_CENTER
		);

		// Version
		dc.drawText(
			width / 2,
			height * 0.78,
			Graphics.FONT_XTINY,
			_versionLabel
				+ " "
				+ _version,
			Graphics.TEXT_JUSTIFY_CENTER
		);
	}

    function onHide() as Void {
    }
}