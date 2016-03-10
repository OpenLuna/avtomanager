function getCSRFTokenValue() {
    return $('input[name="csrfmiddlewaretoken"]').val()
}

$('body').bind('ajaxSend', function(elm, xhr, s){
   if (s.type == 'POST') {
      xhr.setRequestHeader('X-CSRF-Token', getCSRFTokenValue());
   }
});