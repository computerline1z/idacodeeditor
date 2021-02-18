var btn = document.getElementById('send-btn');

// Stop Crtl-s
$(document).bind('keydown', function(e) {
	if (e.ctrlKey && e.which == 83) {
		e.preventDefault();
		//alert('Ctrl+S');
		return false;
	}
});

function stringFromUTF8Array(data) {
	const extraByteMap = [1, 1, 1, 1, 2, 2, 3, 0];
	var count = data.length;
	var str = '';

	for (var index = 0; index < count; ) {
		var ch = data[index++];
		if (ch & 0x80) {
			var extra = extraByteMap[(ch >> 3) & 0x07];
			if (!(ch & 0x40) || !extra || index + extra > count) return null;

			ch = ch & (0x3f >> extra);
			for (; extra > 0; extra -= 1) {
				var chx = data[index++];
				if ((chx & 0xc0) != 0x80) return null;

				ch = (ch << 6) | (chx & 0x3f);
			}
		}

		str += String.fromCharCode(ch);
	}

	return str;
}

let url = 'ws://' + defaultAddress + '/ws';

let wsockClient = {
	sock: null,
	heatbeat: function() {
		const interval = setInterval(function ping() {
		  if (wsockClient.sock.readyState !== WebSocket.OPEN) {
		  	btn.classList.remove('btn-success');
		  	if (!btn.classList.contains('btn-danger'))
		  		btn.classList.add('btn-danger');
		  	console.log('Restart socket')
		  	wsockClient.sock = new WebSocket(url);
		} else {
			btn.classList.remove('btn-danger');
			if (!btn.classList.contains('btn-success'))
		  		btn.classList.add('btn-success');
		}
		  console.log('heatbeat');
		}, 5000);	
	},
	start: function() {
		wsockClient.sock = new WebSocket(url);
		wsockClient.sock.onmessage = function(evt) {
			var cmd = JSON.parse(evt.data);
			if (cmd.action !== 'intelisence') return;

			var wordList = cmd.payload;

			var staticWordCompleter = {
				getCompletions: function(editor, session, pos, prefix, callback) {
					callback(null, [
						...wordList.map(function(word) {
							return {
								caption: word,
								value: word,
								meta: 'static',
							};
						}),
						...session.$mode.$highlightRules.$keywordList.map(function(word) {
							return {
								caption: word,
								value: word,
								meta: 'keyword',
							};
						}),
					]);
				},
			};

			//editor.completers = [staticWordCompleter];
		};
		wsockClient.sock.onclose = function() {
			wsockClient.sock.close();
		};
	},
	send: function() {
		 if (wsockClient.sock.readyState == WebSocket.OPEN) {
			wsockClient.sock.send(editor.getValue());
		 } else {
		 	alert('Socket is not connected !');
		 }
	},
};
wsockClient.start();
wsockClient.heatbeat();
// btn send
btn.addEventListener('click', function() {
	wsockClient.send();
});
