$(document).ready(function () {
	var client = new ZeroClipboard($(".copy"));
	client.on("ready", function (readyEvent) {
		client.on("aftercopy", function (event) {
			alert("Copied to clipboard: " + event.data["text/plain"]);
		});
	});
});
