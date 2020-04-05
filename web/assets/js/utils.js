function api(method, url, data, callback) {
  $.ajax({
      url: '/' + url,
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

function pagination () {
  var table = $('[pagination]');
  var url = table.attr('pagination');

  table.after('<div class="loading" class="mdui-p-y-3 mdui-text-center mdui-text-color-theme-700">数据加载中……</div>');
  api('GET', url, {}, function (r) {
    table.next('.loading').remove();

    for (var i=0; i<r.data.length; i++) {
      var row = r.data[i];

      table.find('tbody').append(
          '<tr>'
        + '  <td>' + row.id + '</td>'
        + '  <td>'
        + '    <a href="/play/' + row.slug + '" target="_blank" class="mdui-text-color-theme-100">' + row.title + '</a>'
        + '  </td>'
        + '  <td>' + row.tags + '</td>'
        + '  <td>' + dateformat(row.created_at) + '</td>'
        + '  <td>'
        + '    <a href="/video/' + row.id + '" class="mdui-btn mdui-btn-icon"><i class="mdui-icon material-icons">edit</i></a>'
        + '    <a class="mdui-btn mdui-btn-icon"><i class="mdui-icon material-icons">delete</i></a>'
        + '  </td>'
        + '</tr>'
      )
    }
  })
}

function dateformat(date) {
  var date = new Date(date);
  return date.getFullYear() + '-' + date.getMonth() + '-' + date.getDate() + ' ' + date.getHours() + ':' + date.getMinutes()
}
