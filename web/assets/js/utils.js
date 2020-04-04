function api(method, url, data, callback) {
  $.ajax({
      url: url,
      data: data,
      type: method,
      beforeSend: function(xhr){
        xhr.setRequestHeader('API-Token', SECRET);
        xhr.setRequestHeader('API-Version', VERSION);
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
