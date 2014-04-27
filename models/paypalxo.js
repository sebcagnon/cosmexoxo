// code taken from node-paypalxo module on github
// npm module is not updated anymore (missed a patch) so copied it here
// original URL: https://github.com/jeffharrell/node-paypalxo

'use strict';


var https = require('https'),
	util = require('util'),
	querystring = require('querystring'),
	paypalxo = {
		user: null,
		pwd: null,
		signature: null,
		version: null,
		appId: null,
		requestFormat: 'JSON',
		responseFormat: 'JSON',
		useSandbox: false
	},
	endPoints = {
		www: {
			url: 'www.paypal.com',
			sandbox: 'sandbox.paypal.com'
		},
		nvp: {
			url: 'api-3t.paypal.com',
			sandbox: 'api-3t.sandbox.paypal.com'
		},
		svcs: {
			url: 'svcs.paypal.com',
			sandbox: 'svcs.sandbox.paypal.com'
		}
	};


function getUrlByType(type) {
	var endPoint = endPoints[type],
		isSandbox = paypalxo.useSandbox;

	if (endPoint) {
		return (isSandbox) ? endPoint.sandbox : endPoint.url;
	}
}


function makePostRequest(options, data, callback) {
	// Initiate the HTTPS request
	var request = https.request(options, function(response) {
		var body = [];

		response.on('data', function(chunk) {
			body.push(chunk);
		});

		response.on('end', function () {
			callback(null, body.join(''));
		});
	});

	request.on('error', function (e) {
		process.nextTick(function () {
			callback(e);
		});
	});

	request.write(data);
	request.end();

	return request;
}


function nvpRequest(name, data, callback) {
	var postData, httpsOptions;

	// Add the authentication info to the body of the POST data
	data.method = name;
	data.user = paypalxo.user;
	data.pwd = paypalxo.pwd;
	data.signature = paypalxo.signature;
	data.version = paypalxo.version;

	// Convert the POST to a URL string
	postData = querystring.stringify(data);

	httpsOptions = {
		host: getUrlByType('nvp'),
		path: '/nvp',
		method: 'POST',
		headers: {
			'Content-Type': 'application/x-www-form-urlencoded',
			'Content-Length': postData.length
		}
	};

	// Fire off a POST request
	return makePostRequest(httpsOptions, postData, function (err, raw) {
		var nvp = querystring.parse(raw);

		// An error occurred
		if (err || nvp.ACK !== 'Success') {
			process.nextTick(function () {
				callback(err || nvp);
			});
		// The parsed response is succesful
		} else {
			process.nextTick(function () {
				callback(null, nvp, raw.toString());
			});
		}
	});
}



function svcsRequest(path, data, callback) {
	var postData, httpsOptions, contentType;

	// Convert the POST to a JSON string
	if (paypalxo.requestFormat === 'JSON') {
		contentType = 'application/json';
		postData = JSON.stringify(data); 
	} else {
		contentType = 'application/x-www-form-urlencoded';
		postData = querystring.stringify(data);
	}

	// Add the authentication info to the body of the POST data
	httpsOptions = {
		host: getUrlByType('svcs'),
		path: '/' + path,
		method: 'POST',
		headers: {
			'Content-Type': contentType,
			'Content-Length': postData.length,
			'X-PAYPAL-SECURITY-USERID': paypalxo.user,
			'X-PAYPAL-SECURITY-PASSWORD': paypalxo.pwd,
			'X-PAYPAL-SECURITY-SIGNATURE': paypalxo.signature,
			'X-PAYPAL-REQUEST-DATA-FORMAT': paypalxo.requestFormat,
			'X-PAYPAL-RESPONSE-DATA-FORMAT': paypalxo.responseFormat,
			'X-PAYPAL-APPLICATION-ID': paypalxo.appId
		}
	};

	// Fire off a POST request
	return makePostRequest(httpsOptions, postData, function (err, raw) {
		var json = JSON.parse(raw),
			responseEnvelope = json && json.responseEnvelope;

		// An error occurred
		if (err || responseEnvelope.ack !== 'Success') {
			process.nextTick(function () {
				callback(err || json);
			});
		// The parsed response is succesful
		} else {
			process.nextTick(function () {
				callback(null, json, raw.toString());
			});
		}
	});
}


/* Express Checkout */
paypalxo.ec = {};


paypalxo.ec.setExpressCheckout = function (data, callback) {
	return nvpRequest('SetExpressCheckout', data, callback);
};


paypalxo.ec.getExpressCheckoutDetails = function (data, callback) {
	return nvpRequest('GetExpressCheckoutDetails', data, callback);
};


paypalxo.ec.doExpressCheckoutPayment = function (data, callback) {
	return nvpRequest('DoExpressCheckoutPayment', data, callback);
};


paypalxo.ec.createRecurringPaymentsProfile = function (data, callback) {
	return nvpRequest('CreateRecurringPaymentsProfile', data, callback);
};


paypalxo.ec.getLoginURL = function (token, isCommit) {
	var url  = 'https://';
		url += getUrlByType('www');
		url += '/cgi-bin/webscr?cmd=_express-checkout&token=';
		url += token;
		url += isCommit ? '&useraction=commit' : '';

	return url;
};



/* Adaptive Payments */
paypalxo.ap = {};


paypalxo.ap.pay = function (data, callback) {
	return svcsRequest('AdaptivePayments/Pay', data, callback);
};


paypalxo.ap.paymentDetails = function (data, callback) {
	return svcsRequest('AdaptivePayments/PaymentDetails', data, callback);
};


paypalxo.ap.getLoginURL = function (payKey) {
	var url  = 'https://';
		url += getUrlByType('www');
		url += '/cgi-bin/webscr?cmd=_ap-payment&paykey=';
		url += payKey;

	return url;
};




/* Export methods */
module.exports = paypalxo;
