var me = this;
socket.on('quotation', function (data) {
  if (me.quotations.length > 0) {
    $.each(data, function () {
      var quo = me.quotations[this[0]];
      quo.lastModified = new Date();

      for (var i = 1; i < this.length; i++) {
        var field = me._fields[i - 1];
        switch (field) {
          case 'buys':
          case 'sells':
            var cnt = 0;
            $.each(this[i], function () {
              quo[field][cnt] += cnt % 2 ? this : this / Math.pow(10, quo.digits);
              ++cnt;
            });
            break;
          case 'details':
            var cnt = 0;
            $.each(this[i], function () {
              quo[field][cnt] += (cnt % 4) != 1 ? this : this / Math.pow(10, quo.digits);
              ++cnt;
            });
            break;
          case 'volume':
          case 'amount':
            quo[field] += this[i];
            break;
          case 'price':
            quo.updown = this[i];
          default:
            quo[field] += this[i] / Math.pow(10, quo.digits);
        }
      }

      if (quo.last_settle && quo.price) {
        quo.fluctuation = quo.price - quo.last_settle;
        quo.fluctuationRate = parseFloat((quo.fluctuation / quo.last_settle).toFixed(4));
      } else {
        delete quo.fluctuation;
        delete quo.fluctuationRate;
      }
    });

    $.each(me.quotations, function () {
      if (new Date() - this.lastModified > 2000) this.updown = 0;
    });
  } else {
    $.each(data, function () {
      if ('string' != typeof this[1]) return ;

      var quo = me.quotations[this[0]] = {};
      quo.symbol = me._symbols[this[0]];
      quo.name = this[1];
      quo.digits = this[2];
      for (var i = 3; i < this.length; i++) {
        var field = me._fields[i - 3];
        quo[field] = this[i];
        switch (field) {
          case 'volume':
          case 'amount':
          case 'buys':
          case 'sells':
          case 'details':
            break;
          default:
            quo[field] = quo[field] / Math.pow(10, quo.digits);
        }
      }

      quo.updown = 0;

      if (quo.last_settle && quo.price) {
        quo.fluctuation = quo.price - quo.last_settle;
        quo.fluctuationRate = parseFloat((quo.fluctuation / quo.last_settle).toFixed(4));
      }
    });
  }

  $.each(me.quotations, function (idx, q) {
    if (!q) return;

    function gen(f) {
      if (q[f]) {
        q[f + '_data'] = [];
        for (var i = 0; i < q[f].length; i += 2) {
          if (q[f][i] > 0) {
            q[f + '_data'].push({ price: q[f][i], volume: q[f][i + 1]});
          }
        }
      }
    }

    gen('buys');
    gen('sells');
    q.sells_data.reverse();

    q.details_data = q.details_data || [];
    var tmp = [];
    var clear;
    for (var i = 0; i < q.details.length - 4; i += 4) {
      if (q.details[i + 2] > (q.last_volume || 0) && q.details[i + 6] > 0) {
        var vol = q.details[i + 2] - q.details[i + 6],
          pos = q.details[i + 3] - q.details[i + 7];

        if (vol < 0) {
          clear = true;
          vol = q.details[i + 2];
          pos = q.details[i + 3];
        }

        tmp.push({
          time: new Date(q.details[i] * 1000),
          price: q.details[i + 1],
          volume: vol,
          position: pos
        });

        if (clear) break;
      }
    }

    q.details_data = clear ? tmp : tmp.concat(q.details_data);
    if (q.details_data.length > 50) q.details_data = q.details_data.slice(0, 50);

    q.last_volume = q.volume;
  });

  $(document).trigger('quotation', [me.quotations]);
});



