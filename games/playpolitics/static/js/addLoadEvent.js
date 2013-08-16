/*
 Allows you to add multiple window.onLoad() functions.
 Usage:
    addLoadEvent(nameOfSomeFunctionToRunOnPageLoad);
    addLoadEvent(function() {
      // more code to run on page load 
    });

  From http://www.htmlgoodies.com/beyond/javascript/article.php/3724571/Using-Multiple-JavaScript-Onload-Functions.htm
*/
function addLoadEvent(func) {
  var oldonload = window.onload;
  if (typeof window.onload != 'function') {
    window.onload = func;
  } else {
    window.onload = function() {
      if (oldonload) {
        oldonload();
      }
      func();
    }
  }
}
