/*! Select2 4.0.13 | https://github.com/select2/select2/blob/master/LICENSE.md */

!(function () {
	if (jQuery && jQuery.fn && jQuery.fn.select2 && jQuery.fn.select2.amd)
		var e = jQuery.fn.select2.amd;
	e.define("select2/i18n/bs", [], function () {
		function e(e, n, r, t) {
			return e % 10 == 1 && e % 100 != 11
				? n
				: e % 10 >= 2 && e % 10 <= 4 && (e % 100 < 12 || e % 100 > 14)
				? r
				: t;
		}
		return {
			errorLoading: function () {
				return "Preuzimanje nije uspijelo.";
			},
			inputTooLong: function (n) {
				var r = n.input.length - n.maximum,
					t = "Obrišite " + r + " simbol";
				return (t += e(r, "", "a", "a"));
			},
			inputTooShort: function (n) {
				var r = n.minimum - n.input.length,
					t = "Ukucajte bar još " + r + " simbol";
				return (t += e(r, "", "a", "a"));
			},
			loadingMore: function () {
				return "Preuzimanje još rezultata…";
			},
			maximumSelected: function (n) {
				var r = "Možete izabrati samo " + n.maximum + " stavk";
				return (r += e(n.maximum, "u", "e", "i"));
			},
			noResults: function () {
				return "Ništa nije pronađeno";
			},
			searching: function () {
				return "Pretraga…";
			},
			removeAllItems: function () {
				return "Uklonite sve stavke";
			},
		};
	}),
		e.define,
		e.require;
})();
