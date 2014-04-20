//http://www.baring.cn:3000/js/yt.data.js
success: function (data) {
    curChartReq = null;

    var chartdata = {};
    chartdata.total = data[0];

    var ohlc = data[1];
    ohlcDigits = ohlc[0];

    chartdata.ohlc = [];
    chartdata.ohlc.digits = ohlcDigits;
    var lastitem;
    for (var i = 0; i < chartdata.total; i++) {
        var item = [];
        for (var j = 1; j < ohlc.length; j++) {
            item.push(ohlc[j][i]);
        }

        if (i > 0) {
            for (var j = 0; j < item.length; j++) {
                item[j] += lastitem[j];
                lastitem[j] = item[j];
            }
        } else {
            lastitem = [];
            item.forEach(function (fld) { lastitem.push(fld); });
        }

        var f = Math.pow(10, ohlcDigits);
        for (var j = 1; j < item.length; j++)
            item[j] /= f;

        item[0] *= 1000;
        chartdata.ohlc.push(item);
    }

    for (var idx = 2; idx < data.length; idx++) {
        var netdata = data[idx];
        var digits = netdata[1];
        var factor = Math.pow(10, digits);
        chartdata[netdata[0]] = [];
        chartdata[netdata[0]].digits = digits;

        var ii = netdata[0].indexOf('(');
        var zname = netdata[0].slice(0, ii < 0 ? undefined : ii);

        for (var i = 2; i < netdata.length; i++) {
            var sdata = netdata[i];
            if (!sdata[0] || sdata[0].length == 0) sdata[0] = zname;
            var ss = { name: sdata[0], type: sdata[1], data: [] };
            if (sdata[2]) {
                var color = sdata[2];
                var r = (color & 0xff) << 16;
                var g = (color & 0xff00);
                var b = (color & 0xff0000) >> 16;

                var ll = "000000";
                ss.color = r + g + b;
                ss.color = ss.color.toString(16);
                ss.color = "#" + ll.slice(ss.color.length) + ss.color;
            }

            var lastitem;
            var sarr = sdata[3];
            for (var j = 0; j < chartdata.total; j++) {
                var item = [chartdata.ohlc[j][0], sarr[j]];

                if (j > 0) {
                    item[1] += lastitem[1];
                    lastitem[1] = item[1];
                } else {
                    lastitem = [item[0], item[1]];
                }

                item[1] /= factor;
                ss.data.push(item);
            }

            chartdata[netdata[0]].push(ss);
        }
    }

