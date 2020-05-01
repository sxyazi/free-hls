function api(method, url, data, callback) {
  return $.ajax({
      url: '/' + url,
      data: data,
      type: method,
      processData: !(data instanceof FormData),
      contentType: data instanceof FormData ? false : 'application/x-www-form-urlencoded',
      beforeSend: function (xhr) {
        xhr.setRequestHeader('API-Token', window.SECRET || '');
        xhr.setRequestHeader('API-Version', window.VERSION || '');
      },
      success: function(r) {
        var ok = r[0], data = r[1];
        if (ok) {
          return callback(data)
        }

        snackbar(data)
      },
      error: function () {
        snackbar('Request failed: connection error')
      }
  });
}

function snackbar(msg, callback) {
  mdui.snackbar({
    message: msg,
    position: 'right-top',
    onClosed: function () {
      callback && callback()
    }
  })
}

function pagination(elem, callback, page) {
  var p = elem.attr('pagination').split(':'), method = p[0], url = p[1];
  var rel = elem.attr('index') ? '[index="' + elem.attr('index') + '"]' : '';
  url += (url.indexOf('?') == -1 ? '?' : '&') + 'page=' + (page || 1);

  $('.paginate-loading' + rel).show();
  api(method, url, {}, function (r) {
    var pre = r.pre || r.length || 0,
        cur = r.page || 1,
        count = r.count || r.length || 0,
        pages = Math.ceil(count / pre) || 1,
        paginator = '<span>共 ' + count + ' 项</span><div class="links">';

    // 上一页
    if (cur > 1) {
      paginator += '<a href="#" switch="' + (cur - 1) + '" class="mdui-ripple mdui-text-color-theme-500">上一页</a>';
    }

    // 最前2页
    if (cur > 3) {
      for (var i=1; i<=2; i++) paginator += '<a href="#" class="mdui-ripple mdui-text-color-theme-500">' + i + '</a>';
      paginator += '<a class="mdui-ripple mdui-text-color-theme-500">···</a>';
    }

    // 当前页-3
    for (var i=3, j=cur; i>0 && j>1; i--, j--) {
      paginator += '<a href="#" switch="' + (cur - i) + '" class="mdui-ripple mdui-text-color-theme-500">' + (cur - i) + '</a>';
    }

    // 当前页
    if (cur != pages) {
      paginator += '<a href="#" class="mdui-ripple mdui-text-color-theme-400">' + cur + '</a>';
    }

    // 当前页+3
    for (var i=0, j=cur+1; i<3 && j<=pages; i++, j++) {
      paginator += '<a href="#" switch="' + j + '" class="mdui-ripple mdui-text-color-theme-500">' + j + '</a>';
    }

    // 最后2页
    if (cur < pages - 3) {
      paginator += '<a class="mdui-ripple mdui-text-color-theme-500">···</a>';
      for (var i=2; i>0; i--) paginator += '<a href="#" class="mdui-ripple mdui-text-color-theme-500">' + (pages - i + 1) + '</a>';
    }

    // 下一页
    if (cur < pages) {
      paginator += '<a href="#" switch="' + (cur + 1) + '" class="mdui-ripple mdui-text-color-theme-500">下一页</a>';
    }

    $('.paginate-loading' + rel).hide();
    $('.paginate-container' + rel).html(callback(r.data || r));
    $('.paginator' + rel).html(paginator + '</div>');
    $('.paginator[switch]' + rel).click(function () {
      pagination(elem, callback, $(this).attr('switch'));
    });
  });

  return function () { pagination(elem, callback, page); }
}

function dateformat(date) {
  var date = new Date(date);
  var pad = function (s) { return ('0' + s).substr(-2); }
  return date.getFullYear() + '-' + pad(date.getMonth()) + '-' + pad(date.getDate()) + ' ' + pad(date.getHours()) + ':' + pad(date.getMinutes())
}
