/*! Select2 4.0.13 | https://github.com/select2/select2/blob/master/LICENSE.md */

!(function () {
	if (jQuery && jQuery.fn && jQuery.fn.select2 && jQuery.fn.select2.amd)
		var e = jQuery.fn.select2.amd;
	e.define("select2/i18n/it", [], function () {
		return {
			errorLoading: function () {
				return "I risultati non possono essere caricati.";
			},
			inputTooLong: function (e) {
				var n = e.input.length - e.maximum,
					t = "Per favore cancella " + n + " caratter";
				return (t += 1 !== n ? "i" : "e");
			},
			inputTooShort: function (e) {
				return (
					"Per favore inserisci " +
					(e.minimum - e.input.length) +
					" o più caratteri"
				);
			},
			loadingMore: function () {
				return "Caricando più risultati…";
			},
			maximumSelected: function (e) {
				var n = "Puoi selezionare solo " + e.maximum + " element";
				return 1 !== e.maximum ? (n += "i") : (n += "o"), n;
			},
			noResults: function () {
				return "Nessun risultato trovato";
			},
			searching: function () {
				return "Sto cercando…";
			},
			removeAllItems: function () {
				return "Rimuovi tutti gli oggetti";
			},
		};
	}),
		e.define,
		e.require;
})();
